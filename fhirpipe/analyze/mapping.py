import os
import json
from collections import defaultdict

from fhirpipe.extract.graphql import build_resources_query, run_graphql_query
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin

from .attribute import Attribute


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


def analyze_mapping(resource_mapping):
    analysis_attributes = []
    columns = set()
    joins = set()
    for attribute_mapping in resource_mapping["attributes"]:
        attribute, attr_columns, attr_joins = analyze_attribute(attribute_mapping)
        analysis_attributes.append(attribute)
        columns = columns.union(attr_columns)
        joins = joins.union(attr_joins)

    return analysis_attributes, columns, joins


def analyze_attribute(attribute_mapping):
    attribute = Attribute(
        path=attribute_mapping["path"], columns=[], static_inputs=[], merging_script=None
    )
    columns = set()
    joins = set()
    for input in attribute_mapping["inputs"]:
        if input["sqlValue"]:
            sql = input["sqlValue"]
            cur_col = SqlColumn(sql["table"], sql["column"], sql["owner"])

            if input["script"]:
                cur_col.cleaning_script = CleaningScript(input["script"])

            if input["conceptMapId"]:
                cur_col.concept_map = ConceptMap(input["conceptMapId"])

            for join in sql["joins"]:
                tables = join["tables"]
                col1 = SqlColumn(tables[0]["table"], tables[0]["column"], tables[0]["owner"])
                col2 = SqlColumn(tables[1]["table"], tables[1]["column"], tables[1]["owner"])
                joins.add(SqlJoin(col1, col2))

            columns.add(cur_col)
            attribute.add_column(cur_col)

        elif input["staticValue"]:
            attribute.add_static_input(input["staticValue"])

    if attribute_mapping["mergingScript"]:
        attribute.merging_script = MergingScript(attribute_mapping["mergingScript"])

    return attribute, columns, joins


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
