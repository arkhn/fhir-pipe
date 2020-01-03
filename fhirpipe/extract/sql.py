import psycopg2  # noqa
import cx_Oracle  # noqa
import pandas as pd

import fhirpipe
from fhirpipe.utils import get_table_name


def build_sql_query(columns, joins, table_name):
    """
    """
    sql_cols = ", ".join(columns)
    sql_joins = "\n".join(
        [
            f"LEFT JOIN {get_table_name(join_target)} ON {join_source}={join_target}"
            for join_source, join_target in joins
        ]
    )
    return f"SELECT {sql_cols}\nFROM {table_name}\n{sql_joins}"


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
