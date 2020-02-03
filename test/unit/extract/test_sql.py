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
        "SELECT ADMISSIONS.LANGUAGE, PATIENTS.DOD, PATIENTS.SUBJECT_ID\n"
        "FROM PATIENTS\n"
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
