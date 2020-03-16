import os
import json
from typing import Dict, List
from collections import defaultdict

from fhirpipe.extract.graphql import build_resources_query, run_graphql_query
from fhirpipe.utils import new_col_name
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin


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
            f"resource {resource_mapping['definitionId']}."
        )

    return SqlColumn(
        resource_mapping["primaryKeyTable"],
        resource_mapping["primaryKeyColumn"],
        resource_mapping["primaryKeyOwner"],
    )


def find_cols_joins_maps_scripts(resource_mapping):
    """
    Run through the attributes of a resource mapping to find:
    - All columns name to select
    - All joins necessary to collect the data
    - All the scripts used in the mapping
    - All the concept maps used in the mapping

    args:
        resource_mapping: the mapping dict for a single resoure.
        concept_maps: the concept maps used in the mapping and on which columns they
            are used.
        cleaning_scripts: the cleaning scripts used in the mapping and on which columns they
            are used.
        merging_scripts: the merging scripts used in the mapping and on which columns they
            are used.

    return:
        cols: the columns of the source DB that should be used in the fhir resource.
        joins: the joins used in the mapping (ie how to use a column which does not
            come from the primary key table).
    """
    cols = set()
    joins = set()
    concept_maps: Dict[str, ConceptMap] = {}
    cleaning_scripts: Dict[str, CleaningScript] = {}
    merging_scripts: List[MergingScript] = []

    for attribute in resource_mapping["attributes"]:
        cols_merging = []
        static_values = []
        for input in attribute["inputs"]:
            if input["sqlValue"]:
                sql = input["sqlValue"]
                cur_col = SqlColumn(sql["table"], sql["column"], sql["owner"])
                column_name = str(cur_col)
                cols.add(cur_col)

                if input["script"]:
                    # This is a hack to avoid a linting error about complexity too high (>10)
                    # It initializes the cleaning script if it does not exist
                    cleaning_scripts[input["script"]] = cleaning_scripts.get(
                        input["script"], CleaningScript(input["script"])
                    )
                    cleaning_scripts[input["script"]].columns.append(column_name)
                    column_name = new_col_name(input["script"], column_name)

                if input["conceptMapId"]:
                    # This is a hack to avoid a linting error about complexity too high (>10)
                    # It initializes the concept map if it does not exist
                    concept_maps[input["conceptMapId"]] = concept_maps.get(
                        input["conceptMapId"], ConceptMap.fetch(input["conceptMapId"])
                    )
                    concept_maps[input["conceptMapId"]].columns.append(column_name)
                    column_name = new_col_name(input["conceptMapId"], column_name)

                cols_merging.append(column_name)

                for join in sql["joins"]:
                    tables = join["tables"]
                    col1 = SqlColumn(tables[0]["table"], tables[0]["column"], tables[0]["owner"])
                    col2 = SqlColumn(tables[1]["table"], tables[1]["column"], tables[1]["owner"])
                    cur_join = SqlJoin(col1, col2)
                    joins.add(cur_join)

            elif input["staticValue"]:
                static_values.append(input["staticValue"])

        if attribute["mergingScript"]:
            merging_script = MergingScript(attribute["mergingScript"])
            merging_script.columns = cols_merging
            merging_script.static_values = static_values
            merging_scripts.append(merging_script)

    return cols, joins, concept_maps.values(), cleaning_scripts.values(), merging_scripts


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
        join_source = join.left
        join_target = join.right

        # Get table names
        source_table = join_source.table_name()
        target_table = join_target.table_name()

        # Add the join in the join_graph
        graph[source_table].append(target_table)

    return graph
