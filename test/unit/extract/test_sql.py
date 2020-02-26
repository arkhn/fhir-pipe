from unittest import mock
from pytest import raises

from test.unit.conftest import mock_config

import fhirpipe.extract.sql as sql


def test_build_sql_filters():
    primary_key_column = "owner.table.col"
    primary_key_values = [1, 2, 3]

    filters = sql.build_sql_filters(primary_key_column, primary_key_values)

    assert filters == "\nWHERE owner.table.col IN (1, 2, 3)"

    primary_key_values = [123]

    filters = sql.build_sql_filters(primary_key_column, primary_key_values)

    assert filters == "\nWHERE owner.table.col=123"

    filters = sql.build_sql_filters(primary_key_column, None)

    assert filters is None


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


@mock.patch("fhirpipe.extract.graphql.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.extract.sql.psycopg2.connect")
@mock.patch("fhirpipe.extract.sql.cx_Oracle.connect")
def test_get_connection(mock_oracle_connect, mock_postgres_connect):
    # With provided credenials
    creds = {"creds": "creds"}
    # c = sql.get_connection(credentials=creds, connection_type="postgres")
    # print(c)
    with sql.get_connection(credentials=creds, connection_type="postgres"):
        mock_postgres_connect.assert_called_once_with(creds="creds")
        mock_postgres_connect.reset_mock()

    with raises(AssertionError, match="credentials for non postgres DB not supported"):
        with sql.get_connection(credentials=creds, connection_type="oracle"):
            pass

    # With config file
    with sql.get_connection(connection_type="postgres"):
        mock_postgres_connect.assert_called_once_with(
            "postgres_arg1", "postgres_arg2", kwarg1="postgres_kwarg1", kwarg2="postgres_kwarg2"
        )
        mock_postgres_connect.reset_mock()

    with sql.get_connection(connection_type="oracle"):
        mock_oracle_connect.assert_called_once_with(
            "oracle_arg1", "oracle_arg2", kwarg1="oracle_kwarg1", kwarg2="oracle_kwarg2"
        )
        mock_oracle_connect.reset_mock()

    with raises(ValueError, match="Config specifies a wrong database type."):
        with sql.get_connection(connection_type="wrong_db_type"):
            pass
