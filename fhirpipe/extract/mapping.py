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
    from_file=None, selected_source=None, selected_resources=None, selected_labels=None
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
    if selected_source is None and from_file is None:
        raise ValueError("You should provide selected_source or from_file")

    if from_file:
        return get_mapping_from_file(from_file, selected_resources, selected_labels)

    else:
        return get_mapping_from_graphql(selected_source, selected_resources, selected_labels)


def get_mapping_from_file(path, selected_resources, selected_labels):
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)

    with open(path) as json_file:
        mapping = json.load(json_file)

    resources = [
        r
        for r in mapping["resources"]
        if (selected_resources is None or r["definitionId"] in selected_resources)
        and (selected_labels is None or r["label"] in selected_labels)
    ]

    return resources


def get_mapping_from_graphql(selected_source, selected_resources, selected_labels):
    # Build the query
    query = build_resources_query(selected_source, selected_resources, selected_labels)

    # Run it
    resources = run_graphql_query(query)

    for resource in resources["data"]["resources"]:
        yield resource


def get_primary_key(resource_mapping):
    """
    Return primary key table and column of the provided resource.

    args:
        resource_mapping: the object containing all the mapping rules

    Return:
        A tuple with the table containing the primary key and the primary key column.
    """
    if not resource_mapping["primaryKeyTable"] or not resource_mapping["primaryKeyColumn"]:
        raise ValueError(
            "You need to provide a primary key table and column in the mapping for "
            f"resource {resource_mapping['definition']['type']}."
        )
    main_table = (
        (f"{resource_mapping['primaryKeyOwner']}.{resource_mapping['primaryKeyTable']}")
        if resource_mapping["primaryKeyOwner"]
        else resource_mapping["primaryKeyTable"]
    )
    column = f"{main_table}.{resource_mapping['primaryKeyColumn']}"
    return main_table, column


def find_cols_joins_and_scripts(resource_mapping):
    """
    Run through the attributes of a resource mapping to find:
    - All columns name to select
    - All joins necessary to collect the data
    - All the scripts used in the mapping

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
    # ["script1", (["col1", "col3", ...], [static3]),
    #  "script4", ([col2], [static1, static3, ...]),
    #  ...]
    all_merging_scripts = []

    for attribute in resource_mapping["attributes"]:
        cols_merging = []
        statics = []
        for input in attribute["inputs"]:
            if input["sqlValue"]:
                sql = input["sqlValue"]
                column_name = build_col_name(sql["table"], sql["column"], sql["owner"])
                all_cols.add(column_name)

                if input["script"]:
                    all_cleaning_scripts[input["script"]].append(column_name)
                    column_name = new_col_name(input["script"], column_name)

                cols_merging.append(column_name)

                for join in sql["joins"]:
                    tables = join["tables"]
                    source_col = build_col_name(
                        tables[0]["table"], tables[0]["column"], tables[0]["owner"],
                    )
                    target_col = build_col_name(
                        tables[1]["table"], tables[1]["column"], tables[1]["owner"],
                    )
                    all_joins.add((source_col, target_col))

            elif input["staticValue"]:
                statics.append(input["staticValue"])

        if attribute["mergingScript"]:
            all_merging_scripts.append((attribute["mergingScript"], (cols_merging, statics)))

    return all_cols, all_joins, all_cleaning_scripts, all_merging_scripts


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
