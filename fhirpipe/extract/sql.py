import psycopg2  # noqa
import cx_Oracle  # noqa
import pandas as pd
from collections import defaultdict

import fhirpipe
from fhirpipe.extract.graph import DependencyGraph
from fhirpipe.utils import get_table_name, build_col_name, new_col_name


def build_sql_query(columns, joins, table_name):
    """
    """
    return f"""
        SELECT {", ".join(columns)}
        FROM {table_name}
        {" ".join(
            [f"LEFT JOIN {get_table_name(join_target)} ON {join_source}={join_target}" for join_source, join_target in joins]
        )}
    """


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

    # Reference for each table the columns which belongs to it: {table1: [col1, ...]}
    table_col_idx = {}
    for i, col in enumerate(columns):
        table = get_table_name(col)
        if table not in table_col_idx:
            table_col_idx[table] = []
        table_col_idx[table].append(col)

    head_node = dependency_graph.get(main_table)
    squash_rules = build_squash_rule(head_node, table_col_idx)

    return squash_rules


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
    columns = set()
    joins = set()
    # The following dicts are used to store script names and on which columns
    # they are used.
    # cleaning_scripts has the form
    # {"script1": ["col1", "col3", ...], "script4": [col2], ...}
    cleaning_scripts = defaultdict(list)
    # cleaning_scripts has the form
    # {"script1": (["col1", "col3", ...], [static3]),
    #  "script4": ([col2], [static1, static3, ...]),
    #  ...}
    merging_scripts = defaultdict(list)
    if isinstance(tree, dict):
        # If there are some inputs, we can build the objects to output
        if "inputColumns" in tree.keys() and tree["inputColumns"]:

            # Check if we need to build the object to put in merging_scripts
            need_merge = tree["mergingScript"] is not None
            if need_merge:
                cols_to_merge = ([], [])

            for col in tree["inputColumns"]:

                # If table and column are defined, we have an sql input
                if col["table"] and col["column"]:
                    column_name = build_col_name(
                        col["table"], col["column"], col["owner"]
                    )
                    columns.add(column_name)

                    # If there are joins, add them to the output
                    for join in col["joins"]:
                        source_col = build_col_name(
                            join["sourceTable"],
                            join["sourceColumn"],
                            join["sourceOwner"],
                        )
                        target_col = build_col_name(
                            join["targetTable"],
                            join["targetColumn"],
                            join["targetOwner"],
                        )
                        joins.add((source_col, target_col))

                    # If there is a cleaning script
                    if col["script"]:
                        column_name = build_col_name(
                            col["table"], col["column"], col["owner"]
                        )
                        cleaning_scripts[col["script"]].append(column_name)
                        if need_merge:
                            cols_to_merge[0].append(
                                new_col_name(col["script"], column_name)
                            )
                    # Otherwise, simply add the column name
                    elif need_merge:
                        cols_to_merge[0].append(column_name)

                # If it's a static value add it in case we need it for the merging
                elif col["staticValue"] and need_merge:
                    cols_to_merge[1].append(col["staticValue"])

            # Add merging script to scripts dict if needed
            if tree["mergingScript"]:
                merging_scripts[tree["mergingScript"]].append(cols_to_merge)

        # If no input, we recurse in child
        else:
            return find_cols_joins_and_scripts(tree["attributes"])

    # If the current object is a list, we can repeat the same steps as above for each item
    elif isinstance(tree, list) and len(tree) > 0:
        for t in tree:
            (
                c_children,
                j_children,
                cs_children,
                ms_children,
            ) = find_cols_joins_and_scripts(t)
            columns = columns.union(c_children)
            joins = joins.union(j_children)
            for scr, scr_cols in cs_children.items():
                cleaning_scripts[scr] += scr_cols
            for scr, scr_cols in ms_children.items():
                merging_scripts[scr] += scr_cols

    return columns, joins, cleaning_scripts, merging_scripts


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
    joins_elems = dict()
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


def build_squash_rule(node, table_col_idx):
    """
    Using the dependency graph of the joins on the tables (accessed through the
    head node), regroup (using the id) the columns which should be squashed (ie
    those accessed through a OneToMany join)

    Args:
        node: the node of the source table (which can be relative in recursive calls)
        table_col_idx: a dict [table_name]: list of idx of cols in the SQL response
            which come from this table

    Return:
        [
            (idx cols for source_table),
            [
                (idx cols for join OneToMany n1, [...]),
                (idx cols for join OneToMany n2, [...]),
                ...
            ]
        ]
    """
    # We refer the col indices of the table
    unifying_col_idx = table_col_idx[node.name]

    # Now parse the col indices for each table joined with a OneToMany
    child_rules = []
    for join_node in node.connections:
        # print(node.name, "-<=", join_node.name)
        child_rules.append(build_squash_rule(join_node, table_col_idx))
    return [unifying_col_idx, child_rules]


def get_connection(connection_type: str = None):
    """
    Return a sql connexion depending on the configuration provided in
    config.yml (see root of the project)
    It should be used in a context environment (with get_connection(c) as ...)

    args:
        connection_type (str): a string like "postgres", "oracle". See your
            config file for available values

    return:
        a sql connexion
    """
    sql_config = fhirpipe.global_config["sql"]
    if connection_type is None:
        connection_type = sql_config["default"]
    connection = sql_config[connection_type]

    args = connection["args"]
    kwargs = connection["kwargs"]

    if connection_type == "postgres":
        return psycopg2.connect(*args, **kwargs)
    elif connection_type == "oracle":
        return cx_Oracle.connect(*args, **kwargs)
    else:
        raise ValueError(
            'Config specifies a wrong database type. \
            The only types supported are "postgres" and "oracle".'
        )


def run_sql_query(query, connection_type: str = None, chunksize: int = None):
    """
    Run a sql query after opening a sql connection

    args:
        query (str): a sql query to run
        connection_type (str): the connection type / database to use
        chunksize: If specified, return an iterator where chunksize
            is the number of rows to include in each chunk.

    return:
        the result of the sql query run on the specified connection type
            or an iterator if chunksize is specified
    """
    pd_query = pd.read_sql_query(
        query, get_connection(connection_type), chunksize=chunksize
    )

    # If chunksize is None, we the whole dataframe
    # Note that we still use yield to use the for ... in ... syntax in any case
    if chunksize is None:
        yield pd.DataFrame(pd_query)
    # Otherwise, we return an iterator
    else:
        for chunk_query in pd_query:
            yield pd.DataFrame(chunk_query)
