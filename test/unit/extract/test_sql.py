from pytest import raises

import fhirpipe.extract.sql as sql


def test_build_db_url():
    # With postgres DB
    credentials = {
        "model": "POSTGRES",
        "login": "login",
        "password": "password",
        "host": "host",
        "port": "port",
        "database": "database",
    }
    db_string = sql.build_db_url(credentials)
    assert db_string == "postgresql://login:password@host:port/database"

    # With oracle DB
    credentials["model"] = "ORACLE"
    db_string = sql.build_db_url(credentials)
    assert db_string == "oracle+cx_oracle://login:password@host:port/database"

    # With wrong model
    credentials["model"] = "model"
    with raises(ValueError, match="credentials specifies the wrong database model."):
        sql.build_db_url(credentials)
