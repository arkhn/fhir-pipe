from pytest import raises

import fhirpipe.extract.sql as sql

from test.unit.conftest import mock_config


def test_build_db_string():
    # With postgres DB
    credentials = {
        "model": "postgres",
        "login": "login",
        "password": "password",
        "host": "host",
        "port": "port",
        "database": "database",
    }
    db_string = sql.build_db_string(credentials)
    assert db_string == "postgresql://login:password@host:port/database"

    # With oracle DB
    credentials["model"] = "oracle"
    db_string = sql.build_db_string(credentials)
    assert db_string == "oracle+cx_oracle://login:password@host:port/database"

    # With wrong model
    credentials["model"] = "model"
    with raises(ValueError, match="credentials specifies the wrong database model."):
        sql.build_db_string(credentials)


def test_build_sql_filters():
    # Without filters
    resource_mapping = {"filters": []}
    primary_key_column = "owner.table.col"
    primary_key_values = [1, 2, 3]

    filters = sql.build_sql_filters(resource_mapping, primary_key_column, primary_key_values)

    assert filters == "\nWHERE owner.table.col IN (1, 2, 3)"

    primary_key_values = [123]

    filters = sql.build_sql_filters(resource_mapping, primary_key_column, primary_key_values)

    assert filters == "\nWHERE owner.table.col=123"

    filters = sql.build_sql_filters(resource_mapping, primary_key_column, None)

    assert filters == ""

    # With filters
    resource_mapping = {
        "filters": [
            {
                "sqlColumn": {"owner": "own", "table": "tab", "column": "col"},
                "relation": "<=",
                "value": "10",
            }
        ]
    }

    filters = sql.build_sql_filters(resource_mapping, primary_key_column)

    assert filters == "\nWHERE own.tab.col<=10"

    # With both
    resource_mapping = {
        "filters": [
            {
                "sqlColumn": {"owner": "own", "table": "tab", "column": "col"},
                "relation": "<=",
                "value": "10",
            }
        ]
    }
    primary_key_column = "owner.table.col"
    primary_key_values = [1, 2, 3]

    filters = sql.build_sql_filters(resource_mapping, primary_key_column, primary_key_values)

    assert filters == ("\nWHERE owner.table.col IN (1, 2, 3)" "\nWHERE own.tab.col<=10")

    primary_key_values = [123]

    filters = sql.build_sql_filters(resource_mapping, primary_key_column, primary_key_values)

    assert filters == ("\nWHERE owner.table.col=123" "\nWHERE own.tab.col<=10")


def test_build_sql_query():
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    table = "PATIENTS"

    actual = sql.build_sql_query(cols, joins, table)

    assert actual == (
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n"
        "FROM PATIENTS\n"
        "LEFT JOIN ADMISSIONS ON PATIENTS.SUBJECT_ID=ADMISSIONS.SUBJECT_ID"
    )

    # Without joins
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {}
    table = "PATIENTS"

    actual = sql.build_sql_query(cols, joins, table)

    assert actual == (
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n" "FROM PATIENTS\n"
    )

    # With several joins
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = [
        ("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID"),
        ("PATIENTS.SUBJECT_ID", "MEDICATION.SUBJECT_ID"),
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    table = "PATIENTS"

    actual = sql.build_sql_query(cols, joins, table)

    assert actual == (
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n"
        "FROM PATIENTS\n"
        "LEFT JOIN ADMISSIONS ON PATIENTS.SUBJECT_ID=ADMISSIONS.SUBJECT_ID\n"
        "LEFT JOIN MEDICATION ON PATIENTS.SUBJECT_ID=MEDICATION.SUBJECT_ID"
    )

    # With filters
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    table = "PATIENTS"
    filters = "WHERE PATIENTS.SUBJECT_ID IN (123, 456)\n"

    actual = sql.build_sql_query(cols, joins, table, filters)

    assert actual == (
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n"
        "FROM PATIENTS\n"
        "LEFT JOIN ADMISSIONS ON PATIENTS.SUBJECT_ID=ADMISSIONS.SUBJECT_ID"
        "WHERE PATIENTS.SUBJECT_ID IN (123, 456)\n"
    )
