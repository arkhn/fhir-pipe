import fhirpipe
from fhirpipe.load import sql


def test_get_connection(config):
    connection_type = config.sql.default
    with fhirpipe.load.sql.get_connection(connection_type):
        pass
    with fhirpipe.load.sql.get_connection():
        pass


def test_run(config):
    query = 'SELECT * from patient limit 10;'

    result = sql.run(query)
    assert isinstance(result, list)

    connection_type = config.sql.default
    result = sql.run(query, connection_type)
    assert isinstance(result, list)


def test_batch_run(config):
    # Normal query
    query = 'SELECT * from patient'
    batch_size = 10
    offset = 0
    for batch_idx, offset, rows in fhirpipe.load.sql.batch_run(
            query, batch_size, offset=offset
    ):
        pass

    # Normal query with a connection type
    connection_type = config.sql.default
    for batch_idx, offset, rows in fhirpipe.sql.batch_run(
            query, batch_size, offset=offset, connection=connection_type
    ):
        pass

    # Normal query with a ending ';'
    query = 'SELECT * from patient'
    for _, _, _ in fhirpipe.load.sql.batch_run(query, batch_size, offset=offset):
        pass

    # Query with a Limit statement
    query = 'SELECT * from patient limit 20'
    try:
        for _, _, _ in fhirpipe.load.sql.batch_run(query, batch_size, offset=offset):
            pass
    except NotImplementedError:
        pass
