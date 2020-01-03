import fhirpipe.extract.sql as sql


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
