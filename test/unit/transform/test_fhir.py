import pandas as pd
from pytest import raises

import fhirpipe.transform.fhir as transform

from test.unit import patient_mapping


def test_create_instance(patient_mapping):
    row = {
        "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100092",
        "map_gender_PATIENTS.GENDER": "male",
        "clean_date_PATIENTS.DOB": "2012-12-12",
        "ADMISSIONS.LANGUAGE": "ENGL",
        "ADMISSIONS.HADM_ID": "111",
        "SERVICES.ROW_ID": "2345",
    }
    resource_structure = patient_mapping
    actual = transform.create_instance(row, resource_structure)

    assert actual == {
        "id": actual["id"],
        "identifier": [{"value": "100092"}, {"value": "111"}],
        "resourceType": "Patient",
        "language": {"coding": [{"code": "ENGL"}]},
        "gender": "male",
        "birthDate": "2012-12-12",
        "address": {"city": "Paris", "country": "France"},
        "generalPractitioner": [{"identifier": {"value": "2345"}, "type": "HealthcareService"}],
    }


def test_create_resource(patient_mapping):
    rows = pd.DataFrame(
        [
            {
                "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100092",
                "map_gender_PATIENTS.GENDER": "male",
                "clean_date_PATIENTS.DOB": "2012-12-12",
                "ADMISSIONS.LANGUAGE": "ENGL",
                "ADMISSIONS.HADM_ID": "111",
                "SERVICES.ROW_ID": "2345",
            },
            {
                "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100093",
                "map_gender_PATIENTS.GENDER": "female",
                "clean_date_PATIENTS.DOB": "2011-11-11",
                "ADMISSIONS.LANGUAGE": "FREN",
                "ADMISSIONS.HADM_ID": "222",
                "SERVICES.ROW_ID": "2346",
            },
        ]
    )
    resource_structure = patient_mapping
    actual = transform.create_resource(rows, resource_structure)

    assert actual == [
        {
            "id": actual[0]["id"],
            "identifier": [{"value": "100092"}, {"value": "111"}],
            "resourceType": "Patient",
            "language": {"coding": [{"code": "ENGL"}]},
            "gender": "male",
            "birthDate": "2012-12-12",
            "address": {"city": "Paris", "country": "France"},
            "generalPractitioner": [{"identifier": {"value": "2345"}, "type": "HealthcareService"}],
        },
        {
            "id": actual[1]["id"],
            "identifier": [{"value": "100093"}, {"value": "222"}],
            "resourceType": "Patient",
            "language": {"coding": [{"code": "FREN"}]},
            "gender": "female",
            "birthDate": "2011-11-11",
            "address": {"city": "Paris", "country": "France"},
            "generalPractitioner": [{"identifier": {"value": "2346"}, "type": "HealthcareService"}],
        },
    ]


def test_fetch_values_from_dataframe():
    # Without merging script
    row = {
        "PATIENTS.SUBJECT_ID": "123456",
        "PATIENTS.DOB": "20000101",
        "clean_date_PATIENTS.DOB": "2000-01-01",
    }
    mapping_inputs = [
        {
            "script": "clean_date",
            "staticValue": None,
            "sqlValue": {"owner": "", "table": "PATIENTS", "column": "DOB"},
        }
    ]
    merging_script = ""

    value = transform.fetch_values_from_dataframe(row, mapping_inputs, merging_script)

    assert value == "2000-01-01"

    # With a merging script
    row = {
        "PATIENTS.SUBJECT_ID": "123456",
        "clean_phone_PATIENTS.ROW_ID": "0987654321",
        "merge_clean_phone_PATIENTS.ROW_ID_dummy": "value",
    }
    mapping_inputs = [
        {
            "script": "clean_phone",
            "staticValue": None,
            "sqlValue": {"owner": "", "table": "PATIENTS", "column": "ROW_ID", "joins": []},
        },
        {"script": None, "staticValue": "dummy", "sqlValue": None},
    ]
    merging_script = "merge"

    value = transform.fetch_values_from_dataframe(row, mapping_inputs, merging_script)

    assert value == "value"


def test_handle_array_attributes():
    row = {
        "PATIENTS.A": ("A1", "A2", "A3"),
        "PATIENTS.B": "B",
    }
    attributes_in_array = {
        "path1": {
            "mergingScript": "",
            "inputs": [
                {"sqlValue": {"owner": "", "table": "PATIENTS", "column": "A"}, "script": ""}
            ],
        },
        "path2": {
            "mergingScript": "",
            "inputs": [
                {"sqlValue": {"owner": "", "table": "PATIENTS", "column": "B"}, "script": ""}
            ],
        },
    }

    value = transform.handle_array_attributes(attributes_in_array, row)

    assert value == [
        {"path1": "A1", "path2": "B"},
        {"path1": "A2", "path2": "B"},
        {"path1": "A3", "path2": "B"},
    ]

    # With mismatch in lengths
    row = {
        "PATIENTS.A": ("A1", "A2", "A3"),
        "PATIENTS.B": ("B1", "B2"),
    }
    with raises(AssertionError, match="mismatch in array lengths"):
        transform.handle_array_attributes(attributes_in_array, row)


def test_clean_fhir_object():
    dirty = {
        "a": {"b": [{"c": 123}, {"c": 123}, {"c": 123}, {"c": 222}, {"c": 222}]},
        "d": [{"e": {"f": 456}}, {"e": {"f": 456}}, {"e": 456}],
    }
    clean = transform.clean_fhir_object(dirty)

    expected = {
        "a": {"b": [{"c": 123}, {"c": 222}]},
        "d": [{"e": {"f": 456}}, {"e": 456}],
    }

    assert clean == expected


def test_get_position_first_index():
    path = ["identifier", "0", "value"]
    index = transform.get_position_first_index(path)
    assert index == 1

    path = ["identifier", "value"]
    index = transform.get_position_first_index(path)
    assert index is None


def test_get_remove_root_path():
    init_path = "identifier.0.value"
    path = transform.remove_root_path(init_path, 2)
    assert path == "value"
