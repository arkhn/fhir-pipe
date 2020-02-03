import os
import json
from collections import defaultdict

from fhirpipe.extract.graphql import build_resources_query, run_graphql_query
from fhirpipe.utils import (
    build_col_name,
    new_col_name,
    get_table_name,
)


def get_mapping(
    from_file=None, selected_sources=None, selected_resources=None, selected_labels=None
):
    """
    Get all available resources from a pyrog mapping.
    The mapping may either come from a static file or from
    a pyrog graphql API.

    Args:
        source_name: name of the project (eg: Mimic)
        from_file: path to the static file to mock
            the pyrog API response.
    """
    if selected_sources is None and from_file is None:
        raise ValueError("You should provide selected_sources or from_file")

    if from_file:
        return get_mapping_from_file(from_file, selected_resources, selected_labels)

    else:
        return get_mapping_from_graphql(selected_sources, selected_resources, selected_labels)


def get_mapping_from_file(path, selected_resources, selected_labels):
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)

    with open(path) as json_file:
        resources = json.load(json_file)

    resources[:] = [
        r
        for r in resources
        if (selected_resources is None or r["fhirType"] in selected_resources)
        and (selected_labels is None or r["label"] in selected_labels)
    ]

    return resources


def get_mapping_from_graphql(selected_sources, selected_resources, selected_labels):
    # Build the query
    query = build_resources_query(selected_sources, selected_resources, selected_labels)
    # Run it
    resources = run_graphql_query(query)

    for resource in resources["data"]["resources"]:
        yield resource


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
        if "children" in attr_structure and attr_structure["children"]:
            attr_structure["children"][:] = [
                attr for attr in attr_structure["children"] if rec_prune_resource(attr)
            ]
            return len(attr_structure["children"]) > 0
        elif "inputs" in attr_structure and attr_structure["inputs"]:
            return True
        else:
            return False

    elif isinstance(attr_structure, list):
        attr_structure[:] = [attr for attr in attr_structure if rec_prune_resource(attr)]
        return len(attr_structure) > 0

    else:
        raise Exception("attr_structure not a dict nor a list.")


def get_primary_key(resource_structure):
    """
    Return primary key table and column of the provided resource.

    args:
        resource_structure: the object containing all the mapping rules

    Return:
        A tuple with the table containing the primary key and the primary key column.
    """
    if not resource_structure["primaryKeyTable"] or not resource_structure["primaryKeyColumn"]:
        raise ValueError(
            "You need to provide a primary key table and column in the mapping for "
            f"resource {resource_structure['fhirType']}."
        )
    main_table = (
        (f"{resource_structure['primaryKeyOwner']}.{resource_structure['primaryKeyTable']}")
        if resource_structure["primaryKeyOwner"]
        else resource_structure["primaryKeyTable"]
    )
    column = f"{main_table}.{resource_structure['primaryKeyColumn']}"
    return main_table, column


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
        if "attributes" in tree and tree["attributes"]:
            return find_cols_joins_and_scripts(tree["attributes"])
        # If we are not in a leaf, we recurse
        if "children" in tree and tree["children"]:
            return find_cols_joins_and_scripts(tree["children"])

        cols, joins, cleaning, merging = find_cjs_in_leaf(tree)

        all_cols = all_cols.union(cols)
        all_joins = all_joins.union(joins)
        dict_concat(all_cleaning_scripts, cleaning)
        dict_concat(all_merging_scripts, merging)

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(tree, list) and len(tree) > 0:
        for t in tree:
            (c_children, j_children, cs_children, ms_children,) = find_cols_joins_and_scripts(t)

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

    for input in leaf["inputs"]:

        # If table and column are defined, we have an sql input
        if input["sqlValue"]:
            sql = input["sqlValue"]
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
            if input["script"]:
                cleaning_scripts[input["script"]].append(column_name)
                if leaf["mergingScript"]:
                    cols_to_merge[0].append(new_col_name(input["script"], column_name))
            # Otherwise, simply add the column name
            elif leaf["mergingScript"]:
                cols_to_merge[0].append(column_name)

        # If it's a static value add it in case we need it for the merging
        elif input["staticValue"] and leaf["mergingScript"]:
            cols_to_merge[1].append(input["staticValue"])

    # Add merging script to scripts dict if needed
    if leaf["mergingScript"]:
        merging_scripts[leaf["mergingScript"]].append(cols_to_merge)

    return columns, joins, cleaning_scripts, merging_scripts


def build_squash_rules(columns, joins, main_table):
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
    if not isinstance(main_table, str):
        raise AttributeError(
            "Please specify the main table for this FHIR Resource, "
            "usually for example for the resource fhir Patient you would "
            "provide a sql table OWNER.Patients or something like this. "
            "Don't forget to provide the owner if it applies."
        )

    # Build a join graph
    join_graph = build_join_graph(joins)

    squash_rules = rec_build_squash_rules(join_graph, main_table)

    return squash_rules


def rec_build_squash_rules(join_graph, node):
    child_rules = []
    for join_node in join_graph[node]:
        child_rules.append(rec_build_squash_rules(join_graph, join_node))

    return [node, child_rules]


def build_join_graph(joins):
    """
    Transform a join info into SQL fragments and parse the graph of join dependency
    Input:
        {("<owner>.<table>.<col>", "<owner>.<join_table>.<join_col>"), ... }
    Return:
        {
            "<table>": ["<join_table 1>", "<join_table 2>", ...],
            ...
        }
    """
    graph = defaultdict(list)
    for join in joins:
        join_source, join_target = join

        # Get table names
        target_table = get_table_name(join_target)
        source_table = get_table_name(join_source)

        # Add the join in the join_graph
        graph[source_table].append(target_table)

    return graph


def dict_concat(dict_1, dict_2):
    for key, val in dict_2.items():
        dict_1[key] += val


def find_reference_attributes(tree, path=[]):
    """ Function to find attributes that are reference.
    We need this to bind them after having loaded the fhir objects.
    """
    references = []
    if isinstance(tree, dict):

        if "name" in tree:
            if not path or not path[-1] == tree["name"]:
                path.append(tree["name"])

        # If attribute is a reference, we add it to the result list
        if tree["fhirType"] == "Reference":
            references.append(tuple(path))

        # I don't think we can have nested references so
        # if we are not in a leaf, we recurse
        else:
            if "attributes" in tree and tree["attributes"]:
                return find_reference_attributes(tree["attributes"], path[:])
            if "children" in tree and tree["children"]:
                return find_reference_attributes(tree["children"], path[:])

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(tree, list) and len(tree) > 0:
        for t in tree:
            refs = find_reference_attributes(t, path[:])

            references.extend(refs)

    return references
