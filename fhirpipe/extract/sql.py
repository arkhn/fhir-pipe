import pandas as pd


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
