import pandas as pd

from fhirpipe.utils import build_col_name, get_table_name


db_driver = {"POSTGRES": "postgresql", "ORACLE": "oracle+cx_oracle"}


def build_db_url(credentials):
    login = credentials["login"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"]

    try:
        db_handler = db_driver[credentials["model"]]
    except KeyError:
        raise ValueError(
            "credentials specifies the wrong database model. "
            "Only 'POSTGRES' and 'ORACLE' are currently supported."
        )

    return f"{db_handler}://{login}:{password}@{host}:{port}/{database}"


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

    if resource_mapping["filters"]:
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


def run_sql_query(engine, query, chunksize: int = None):
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
    pd_query = pd.read_sql_query(query, con=engine, chunksize=chunksize)

    # If chunksize is None, we return the dataframe for the whole DB
    # Note that we still use yield to use the for ... in ... syntax in any case
    if chunksize is None:
        yield pd.DataFrame(pd_query)
    # Otherwise, we return an iterator
    else:
        for chunk_query in pd_query:
            yield pd.DataFrame(chunk_query)
