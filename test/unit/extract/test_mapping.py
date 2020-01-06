from unittest import mock

import fhirpipe.extract.mapping as mapping

from test.unit.extract import MOCK_FILE, RAW_FHIR_RESOURCE, PRUNED_FHIR_RESOURCE


mock_open = mock.mock_open(read_data=MOCK_FILE)


def test_get_mapping_from_file():
    with mock.patch("builtins.open", mock_open):
        resources = mapping.get_mapping_from_file("path")

    assert [r["name"] for r in resources] == [
        "Patient",
        "Encounter",
    ]


# def test_get_mapping_from_graphql():
#     pass


def test_prune_fhir_resource():
    actual = mapping.prune_fhir_resource(RAW_FHIR_RESOURCE)

    assert actual == PRUNED_FHIR_RESOURCE


def test_find_cols_joins_and_scripts():
    fhir_resource = PRUNED_FHIR_RESOURCE

    cols, joins, cleaning, merging = mapping.find_cols_joins_and_scripts(fhir_resource)

    assert cols == {
        "PATIENTS.DOB",
        "PATIENTS.SUBJECT_ID",
        "PATIENTS.EXPIRE_FLAG",
        "PATIENTS.GENDER",
        "ADMISSIONS.MARITAL_STATUS",
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
    }
    assert joins == {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    assert cleaning == {
        "map_gender": ["PATIENTS.GENDER"],
        "format_date_from_yyyymmdd": ["PATIENTS.DOB", "PATIENTS.DOD"],
        "to_boolean": ["PATIENTS.EXPIRE_FLAG"],
    }
    assert merging == {
        "fake_merging_script": [
            (
                ["map_gender_PATIENTS.GENDER", "PATIENTS.EXPIRE_FLAG"],
                ["fake static value"],
            )
        ]
    }


def test_build_squash_rules():
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID")}
    table = "PATIENTS"

    actual = mapping.build_squash_rules(cols, joins, table)

    assert actual == ["PATIENTS", [["ADMISSIONS", []]]]