import os
import logging
import json
from collections import defaultdict

import fhirpipe.extract.graphql as gql
from fhirpipe.extract.graphql import run_graphql_query
from fhirpipe.extract.graph import DependencyGraph
from fhirpipe.utils import get_table_name, build_col_name, new_col_name, dict_concat


def get_mapping(from_file=None, source_name=None, selected_resources=None):
    """
    Get all available resources from a pyrog mapping.
    The mapping may either come from a static file or from
    a pyrog graphql API.

    Args:
        source_name: name of the project (eg: Mimic)
        from_file: path to the static file to mock
            the pyrog API response.
    """
    if source_name is None and from_file is None:
        raise ValueError("You should provide source_name or from_file")

    if from_file:
        return get_mapping_from_file(from_file)

    else:
        return get_mapping_from_graphql(source_name, selected_resources)


def get_mapping_from_file(path, selected_resources):
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)

    with open(path) as json_file:
        resources = json.load(json_file)
    source_json = resources["data"]["database"]

    if selected_resources is not None:
        source_json["resources"][:] = [
            r for r in source_json["resources"][:] if r["name"] in selected_resources
        ]

    return source_json["resources"]


def get_mapping_from_graphql(source_name, selected_resources):
    # Get Source id from Source name
    sources = run_graphql_query(gql.sources_query)

    try:
        # Look for the source which has the name we want
        selected_source = next(
            s for s in sources["data"]["sources"] if s["name"] == source_name
        )
    except StopIteration:
        logging.error(f"No source with name '{source_name}' found")

    # Get the ids of the resources from the query response
    selected_resource_ids = [
        r["id"]
        for r in selected_source["resources"]
        if r["fhirType"] in selected_resources
    ]

    # Return resources mapping
    for resource_id in selected_resource_ids:
        mapping = run_graphql_query(
            gql.resource_query, variables={"resourceId": resource_id}
        )
        yield mapping["data"]["resource"]


def prune_fhir_resource(resource_structure):
    """ Remove FHIR attributes that have not been mapped
    from resource structure object.
    """
    resource_structure["attributes"][:] = [
        attr for attr in resource_structure["attributes"] if rec_prune_resource(attr)
    ]
    return resource_structure


def rec_prune_resource(attr_structure):
    """ Helper recursive function called by prune_fhir_resource.
    """
    if isinstance(attr_structure, dict):
        if attr_structure["children"]:
            attr_structure["children"][:] = [
                attr for attr in attr_structure["children"] if rec_prune_resource(attr)
            ]
            return len(attr_structure["children"]) > 0
        elif attr_structure["inputs"]:
            return True
        else:
            return False

    elif isinstance(attr_structure, list):
        attr_structure[:] = [
            attr for attr in attr_structure if rec_prune_resource(attr)
        ]
        return len(attr_structure) > 0

    else:
        raise Exception("attr_structure not a dict nor a list.")


def get_primary_key(resource_structure, extended_get=False):
    """
    Analyse a resource mapping rules and return the mapping rule for
    the identifier

    args:
        resource_structure: the object containing all the mapping rules
        extended_get (bool): search for the identifier table not only in
            identifier attributes (default: False)

    Return:
        The table referenced by the identifier mapping rule
    """
    # NOTE this souldn't be needed as user can provide primary key column with Pyrog
    pk = build_col_name(
        resource_structure["primaryKeyTable"],
        resource_structure["primaryKeyColumn"],
        resource_structure["primaryKeyOwner"],
    )
    return resource_structure["primaryKeyTable"], pk


#     targets = []
#     for attribute in resource_structure["attributes"]:
#         if attribute["name"] == "identifier" or extended_get:
#             search_for_input_columns(attribute, targets)

#     if len(targets) < 1:
#         if extended_get:
#             raise AttributeError(
#                 "There is no mapping rule for the identifier of this resource"
#             )
#         else:
#             return get_identifier_table(resource_structure, extended_get=True)
#     else:
#         if len(targets) > 1:
#             logging.warning(
#                 "Warning: Too many choices for the right main table for building SQL request,\
# taking the first one."
#             )
#         return targets[0]


# def search_for_input_columns(obj, targets):
#     """
#     Inspect a mapping object of an identifier and list all tables used
#     in mapping rules

#     args:
#         obj: mapping object of an identifier
#         targets: a list to append the tables found

#     returns:
#         None as the results are appended to the targets list
#     """
#     # NOTE this is only used in get_identifier_table so shouldn't be needed neither

#     if isinstance(obj, dict):
#         if "inputColumns" in obj and len(obj["inputColumns"]) > 0:
#             for input_col in obj["inputColumns"]:
#                 if input_col["table"]:
#                     targets.append(input_col["table"])
#         elif "attributes" in obj:
#             search_for_input_columns(obj["attributes"], targets)
#     elif isinstance(obj, list):
#         for o in obj:
#             search_for_input_columns(o, targets)


def find_cols_joins_and_scripts(tree):
    """
    Run through the dict/tree of a Resource
    To find:
    - All columns name to select
    - All joins necessary to collect the data

    args:
        tree (dict): the fhir specification which has the structure of a tree
        source_table (str): name of the source table, ie the table for which each row
            will create one instance of the considered resource

    return:
        a tuple containing all the columns referenced in the tree and all the joins
        to perform to access those columns
    """
    all_cols = set()
    all_joins = set()
    # The following dicts are used to store script names and on which columns
    # they are used.
    # all_cleaning_scripts has the form
    # {"script1": ["col1", "col3", ...], "script4": [col2], ...}
    all_cleaning_scripts = defaultdict(list)
    # all_merging_scripts has the form
    # {"script1": (["col1", "col3", ...], [static3]),
    #  "script4": ([col2], [static1, static3, ...]),
    #  ...}
    all_merging_scripts = defaultdict(list)
    if isinstance(tree, dict):

        # If we are not in a leaf, we recurse
        if "attributes" in tree.keys() and tree["attributes"]:
            return find_cols_joins_and_scripts(tree["attributes"])
        # If we are not in a leaf, we recurse
        if "children" in tree.keys() and tree["children"]:
            return find_cols_joins_and_scripts(tree["children"])

        cols, joins, cleaning, merging = find_cjs_in_leaf(tree)

        all_cols = all_cols.union(cols)
        all_joins = all_joins.union(joins)
        dict_concat(all_cleaning_scripts, cleaning)
        dict_concat(all_merging_scripts, merging)

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(tree, list) and len(tree) > 0:
        for t in tree:
            (
                c_children,
                j_children,
                cs_children,
                ms_children,
            ) = find_cols_joins_and_scripts(t)

            all_cols = all_cols.union(c_children)
            all_joins = all_joins.union(j_children)
            dict_concat(all_cleaning_scripts, cs_children)
            dict_concat(all_merging_scripts, ms_children)

    return all_cols, all_joins, all_cleaning_scripts, all_merging_scripts


def find_cjs_in_leaf(leaf):
    columns = set()
    joins = set()
    cleaning_scripts = defaultdict(list)
    merging_scripts = defaultdict(list)

    # Check if we need to build the object to put in merging_scripts
    cols_to_merge = ([], []) if leaf["mergingScript"] is not None else None

    for inp in leaf["inputs"]:

        # If table and column are defined, we have an sql input
        if inp["sqlValue"]:
            sql = inp["sqlValue"]
            column_name = build_col_name(sql["table"], sql["column"], sql["owner"])
            columns.add(column_name)

            # If there are joins, add them to the output
            for join in sql["joins"]:
                source_col = build_col_name(
                    join["tables"][0]["table"],
                    join["tables"][0]["column"],
                    join["tables"][0]["owner"],
                )
                target_col = build_col_name(
                    join["tables"][1]["table"],
                    join["tables"][1]["column"],
                    join["tables"][1]["owner"],
                )
                joins.add((source_col, target_col))

            # If there is a cleaning script
            if inp["script"]:
                cleaning_scripts[inp["script"]].append(column_name)
                if leaf["mergingScript"]:
                    cols_to_merge[0].append(new_col_name(inp["script"], column_name))
            # Otherwise, simply add the column name
            elif leaf["mergingScript"]:
                cols_to_merge[0].append(column_name)

        # If it's a static value add it in case we need it for the merging
        elif inp["staticValue"] and leaf["mergingScript"]:
            cols_to_merge[1].append(inp["staticValue"])

    # Add merging script to scripts dict if needed
    if leaf["mergingScript"]:
        merging_scripts[leaf["mergingScript"]].append(cols_to_merge)

    return columns, joins, cleaning_scripts, merging_scripts


def build_squash_rules(columns, joins, main_table):
    """
    """
    if not isinstance(main_table, str):
        raise AttributeError(
            "Please specify the main table for this FHIR Resource,\
            usually for example for the resource fhir Patient you would\
            provide a sql table OWNER.Patients or something like this.\
            Don't forget to provide the owner if it applies"
        )

    # Build a dependcy graph
    dependency_graph = build_graph(joins)

    head_node = dependency_graph.get(main_table)
    squash_rules = build_squash_rule(head_node)

    return squash_rules


def build_squash_rule(node):
    """
    Using the dependency graph of the joins on the tables (accessed through the
    head node), regroup (using the id) the columns which should be squashed (ie
    those accessed through a OneToMany join)

    Args:
        node: the node of the source table (which can be relative in recursive calls)

    Return:
        [
            main table name,
            [
                table1 joined on parent, [...],
                table2 joined on parent, [...],
                ...
            ]
        ]
    """
    child_rules = []
    for join_node in node.connections:
        child_rules.append(build_squash_rule(join_node))

    return [node.name, child_rules]


def build_graph(joins):
    """
    Transform a join info into SQL fragments and parse the graph of join dependency
    Input:
        [(<type_of_join>, "<owner>.<table>.<col>=<owner>.<join_table>.<join_col>"), ... ]
    Return:
        [(
            "<join_table>",
            "<table>.<col> = <join_table>.<join_col>"
        ), ... ],
        graph of dependency of type DependencyGraph
    """
    graph = DependencyGraph()
    for join in joins:
        join_source, join_target = join

        # Get table names
        target_table = get_table_name(join_target)
        source_table = get_table_name(join_source)

        # Add the join in the join_graph
        source_node = graph.get(source_table)
        target_node = graph.get(target_table)
        source_node.connect(target_node)

    return graph
