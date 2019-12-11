import psycopg2  # noqa
import cx_Oracle  # noqa
import logging
import pandas as pd

import fhirpipe_clean
from fhirpipe_clean.extract.graph import DependencyGraph

def build_col_name(table, column, owner=None):
    return "{}{}.{}".format(
        owner + "." if owner is not None else "",
        table,
        column,
    )
def get_table_name(name):
    """
    Extract the table_name from a column specification

    Example:
        Case 1
            OWNER.TABLE.COLUMN -> OWNER.TABLE
        Case 2
            TABLE.COLUMN -> TABLE
    """
    elems = name.split(".")
    if len(elems) == 3:
        return ".".join(name.split(".")[:2])
    elif len(elems) == 2:
        return name.split(".")[0]
    else:
        return None


def build_sql_query(columns, joins, info=None):
    """
    """
    if info is None or not isinstance(info, str):
        raise AttributeError(
            "Please specify the main table for this FHIR Resource,\
            usually for example for the resource fhir Patient you would\
            provide a sql table OWNER.Patients or something like this.\
            Don't forget to provide the owner if it applies"
        )

    table_name = get_table_name(info + ".*")

    return f"""
        SELECT {", ".join(columns)}
        FROM {table_name}
        {" ".join(
            [f"LEFT JOIN {get_table_name(join_target)} ON {join_source}={join_target}" for join_source, join_target in joins]
        )}
    """


def build_squash_rules(columns, joins, info=None):
    """
    """
    if info is None or not isinstance(info, str):
        raise AttributeError(
            "Please specify the main table for this FHIR Resource,\
            usually for example for the resource fhir Patient you would\
            provide a sql table OWNER.Patients or something like this.\
            Don't forget to provide the owner if it applies"
        )

    table_name = get_table_name(info + ".*")

    # Build a dependcy graph
    dependency_graph = build_graph(joins)

    # Reference for each table the columns which belongs to it: {table1: [col1, ...]}
    table_col_idx = {}
    for i, col in enumerate(columns):
        table = get_table_name(col)
        if table not in table_col_idx:
            table_col_idx[table] = []
        table_col_idx[table].append(col.split(".")[-1].lower())

    head_node = dependency_graph.get(table_name)
    squash_rules = build_squash_rule(head_node, table_col_idx)

    return squash_rules


def find_cols_and_joins(tree):
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
    columns = []
    joins = set()
    if isinstance(tree, dict):
        if "inputColumns" in tree.keys() and tree["inputColumns"]:
            for col in tree["inputColumns"]:
                # Check if table and column target are defined
                if col["table"] is not None and col["column"] is not None:
                    column_name = build_col_name(col["table"], col["column"], col["owner"])
                    columns.append(column_name)

                # If there is a join
                if "joins" in col.keys() and len(col["joins"]) > 0:
                    for join in col["joins"]:
                        # Add the join
                        source_col = build_col_name(join["sourceTable"], join["sourceColumn"], join["sourceOwner"])
                        target_col = build_col_name(join["targetTable"], join["targetColumn"], join["targetOwner"])
                        joins.add((source_col, target_col))
                # Else it's a static value and there is nothing to do

        else:  # Recurse in child
            cols_child, joins_child = find_cols_and_joins(tree["attributes"])
            columns += cols_child
            joins = joins.union(joins_child)

    elif isinstance(tree, list) and len(tree) > 0:
        for t in tree:
            cols_children, joins_children = find_cols_and_joins(t)
            columns += cols_children
            joins = joins.union(joins_children)

    return columns, joins


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
    print("build graph")
    print(joins)
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
    :param node: the node of the source table (which can be relative in recursive calls)
    :param table_col_idx: a dict [table_name]: list of idx of cols in the SQL response
        which come from this table
    :return: [
        (idx cols for source_table),
        [
            (idx cols for join OneToMany n1, []),
            (idx cols for join OneToMany n2, []),
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
        connection_type (str): a string like "postgre", "oracle". See your
            config file for available values

    return:
        a sql connexion
    """
    sql_config = fhirpipe_clean.global_config.sql.to_dict()
    if connection_type is None:
        connection_type = sql_config["default"]
    connection = sql_config[connection_type]
    try:
        lib = eval(connection["lib"])
    except NameError:
        logging.warning(f"NameError found, did you import the lib {connection['lib']} ?")
        raise ImportError
    args = connection["args"]
    kwargs = connection["kwargs"]

    return lib.connect(*args, **kwargs)


def batch_run(query, batch_size, offset=0, connection=None):
    """
    Run a query batch per batch, when the query is too big

    args:
        query (str): the query to batch
        batch_size (int): the size of the batch
        offset (int): initial offset (used when restarting a job which stopped
            in the middle)
        connection (str): the connection type / database to use

    return:
        an iterator which computes and returns the results batch per batch
    """
    call_next_batch = True
    batch_idx = 0

    # Remove the ending ';' if any
    if query[-1] == ";":
        query = query[:-1]
    # A query with a limit can't be batch run
    limit_words = ["limit", "fetch next"]
    if any(limit_word in query.lower() for limit_word in limit_words):
        raise NotImplementedError(
            "You currently can't run by batch a query which already has a limit"
            "statement. Error in {}".format(query)
        )

    # Adapt the offset and limit depending of oracle or postgre db
    database_type = fhirpipe_clean.global_config.sql.default
    if database_type == "oracle":
        offset_batch_size_instruction = " OFFSET {} ROWS FETCH NEXT {} ROWS ONLY"
    elif database_type == "postgre":
        offset_batch_size_instruction = " OFFSET {} LIMIT {}"
    else:
        raise RuntimeError(f"{database_type} is not a supported database type.")

    while call_next_batch:
        batch_query = query + offset_batch_size_instruction.format(offset, batch_size)
        batch = run(batch_query, connection)

        call_next_batch = len(batch) >= batch_size
        offset += batch_size
        batch_idx += 1

        yield batch_idx, offset, batch


def run_sql_query(query, connection: str = None):
    """
    Run a sql query after opening a sql connection

    args:
        query (str): a sql query to run
        connection (str): the connection type / database to use

    return:
        the result of the sql query run on the specified connection
    """
    # with get_connection(connection) as connection:
    #     with connection.cursor() as cursor:
    #         cursor.execute(query)
    #         rows = cursor.fetchall()

    #     connection.commit()

    # # Replace None values with '' AND replace date with str representation
    # rows[:] = [[str(el) if el is not None else "" for el in row] for row in rows]
    pd_query = pd.read_sql_query(query, get_connection(connection))
    df = pd.DataFrame(pd_query)
    print(df)
    return df
