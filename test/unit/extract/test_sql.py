from unittest import mock

import fhirpipe
import fhirpipe.extract.sql as sql


def test_build_sql_query():
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    table = "PATIENTS"
    primary_key = None

    actual = sql.build_sql_query(cols, joins, table, primary_key)

    assert actual == (
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n"
        "FROM PATIENTS\n"
        "LEFT JOIN ADMISSIONS ON PATIENTS.SUBJECT_ID=ADMISSIONS.SUBJECT_ID"
    )


def test_get_connection():
    sql.get_connection()

# @mock.patch("fhirpipe.extract.sql.get_script", return_value=mock_get_script)
# def test_run_sql_query():
#     pass
