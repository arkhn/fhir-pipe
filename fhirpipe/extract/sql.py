import psycopg2  # noqa
import cx_Oracle  # noqa
import pandas as pd
from contextlib import contextmanager

import fhirpipe
from fhirpipe.utils import build_col_name, get_table_name


def build_sql_filters(resource_mapping, primary_key_column, primary_key_values=None):
    """
    Build sql WHERE clauses.
    It's used for:
        - running the ETL on a few selected rows.
        - conditionally processing a row.
    """
    filters = ""
    if primary_key_values is not None:
        if len(primary_key_values) == 1:
            filters += f"\nWHERE {primary_key_column}={primary_key_values[0]}"
        else:
            filters += f"\nWHERE {primary_key_column} IN {tuple(primary_key_values)}"

    if "filters" in resource_mapping and resource_mapping["filters"]:
        for filter in resource_mapping["filters"]:
            sql_col = filter["sqlColumn"]
            col_name = build_col_name(sql_col["table"], sql_col["column"], sql_col["owner"])
            filters += f"\nWHERE {col_name}{filter['relation']}{filter['value']}"

    return filters


def build_sql_query(columns, joins, table_name, sql_filters=""):
    """
    Writes the sql query from the information gathered by the Analyzer.
    """
    sql_cols = ", ".join(columns)
    sql_joins = "\n".join(
        [
            f"LEFT JOIN {get_table_name(join_target)} ON {join_source}={join_target}"
            for join_source, join_target in joins
        ]
    )
    return f"SELECT {sql_cols}\nFROM {table_name}\n{sql_joins}{sql_filters}"


@contextmanager
def get_connection(credentials=None, connection_type: str = None):
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
    elif connection_type not in ["postgres", "oracle"]:
        raise ValueError(
            "Config specifies a wrong database type. "
            'The only types supported are "postgres" and "oracle".'
        )

    if credentials is None:
        args = sql_config[connection_type]["args"]
        kwargs = sql_config[connection_type]["kwargs"]
    else:
        assert connection_type == "postgres", "credentials for non postgres DB not supported"
        args = []
        kwargs = credentials

    if connection_type == "postgres":
        connection = psycopg2.connect(*args, **kwargs)
    elif connection_type == "oracle":
        connection = cx_Oracle.connect(*args, **kwargs)

    try:
        yield connection
    finally:
        connection.close()


def run_sql_query(connection, query, chunksize: int = None):
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
    pd_query = pd.read_sql_query(query, connection, chunksize=chunksize)

    # If chunksize is None, we return the dataframe for the whole DB
    # Note that we still use yield to use the for ... in ... syntax in any case
    if chunksize is None:
        yield pd.DataFrame(pd_query)
    # Otherwise, we return an iterator
    else:
        for chunk_query in pd_query:
            yield pd.DataFrame(chunk_query)
