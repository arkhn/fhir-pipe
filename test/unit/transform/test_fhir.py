from unittest import mock
import pandas as pd
from pytest import raises

import fhirpipe.transform.fhir as transform
from fhirpipe.transform.fhir import ARKHN_TERMINOLOGY_SYSTEM


class mockdatetime:
    def strftime(self, _):
        return "now"


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_create_instance(mock_datetime, patient_mapping):
    mock_datetime.now.return_value = mockdatetime()
    row = {
        "map_marital_status_admissions.marital_status": "D",
        "map_gender_PATIENTS.GENDER": "male",
        "clean_date_PATIENTS.DOB": "2000-10-10",
        "patients.row_id": "123",
        "binary_to_bool_1_admissions.hospital_expire_flag": "true",
        "clean_date_patients.dod": "2100-01-01",
    }
    resource_mapping = patient_mapping
    actual = transform.create_instance(row, resource_mapping)

    assert actual == {
        "meta": {
            "lastUpdated": "now",
            "tag": [
                {
                    "system": f"{ARKHN_TERMINOLOGY_SYSTEM}/source",
                    "code": patient_mapping["source"]["id"],
                },
                {"system": f"{ARKHN_TERMINOLOGY_SYSTEM}/resource", "code": patient_mapping["id"]},
            ],
        },
        "id": actual["id"],
        "identifier": [{"value": "123"}],
        "resourceType": "Patient",
        "gender": "male",
        "birthDate": "2000-10-10",
        "deceasedBoolean": "true",
        "deceasedDateTime": "2100-01-01",
        "maritalStatus": {"coding": [{"code": "D"}]},
        "generalPractitioner": [{"type": "/Practitioner/"}],
    }


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_create_resource(mock_datetime, patient_mapping):
    mock_datetime.now.return_value = mockdatetime()
    rows = pd.DataFrame(
        [
            {
                "map_marital_status_admissions.marital_status": "D",
                "map_gender_PATIENTS.GENDER": "male",
                "clean_date_PATIENTS.DOB": "2000-10-10",
                "patients.row_id": "123",
                "binary_to_bool_1_admissions.hospital_expire_flag": "true",
                "clean_date_patients.dod": "2100-01-01",
            },
            {
                "map_marital_status_admissions.marital_status": "P",
                "map_gender_PATIENTS.GENDER": "female",
                "clean_date_PATIENTS.DOB": "2001-11-11",
                "patients.row_id": "124",
                "binary_to_bool_1_admissions.hospital_expire_flag": "false",
                "clean_date_patients.dod": "2101-11-11",
            },
        ]
    )
    resource_mapping = patient_mapping
    actual = transform.create_resource(rows, resource_mapping)

    assert actual == [
        {
            "meta": {
                "lastUpdated": "now",
                "tag": [
                    {
                        "system": f"{ARKHN_TERMINOLOGY_SYSTEM}/source",
                        "code": patient_mapping["source"]["id"],
                    },
                    {
                        "system": f"{ARKHN_TERMINOLOGY_SYSTEM}/resource",
                        "code": patient_mapping["id"],
                    },
                ],
            },
            "id": actual[0]["id"],
            "identifier": [{"value": "123"}],
            "resourceType": "Patient",
            "gender": "male",
            "birthDate": "2000-10-10",
            "deceasedBoolean": "true",
            "deceasedDateTime": "2100-01-01",
            "maritalStatus": {"coding": [{"code": "D"}]},
            "generalPractitioner": [{"type": "/Practitioner/"}],
        },
        {
            "meta": {
                "lastUpdated": "now",
                "tag": [
                    {
                        "system": f"{ARKHN_TERMINOLOGY_SYSTEM}/source",
                        "code": patient_mapping["source"]["id"],
                    },
                    {
                        "system": f"{ARKHN_TERMINOLOGY_SYSTEM}/resource",
                        "code": patient_mapping["id"],
                    },
                ],
            },
            "id": actual[1]["id"],
            "identifier": [{"value": "124"}],
            "resourceType": "Patient",
            "gender": "female",
            "birthDate": "2001-11-11",
            "deceasedBoolean": "false",
            "deceasedDateTime": "2101-11-11",
            "maritalStatus": {"coding": [{"code": "P"}]},
            "generalPractitioner": [{"type": "/Practitioner/"}],
        },
    ]


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_build_metadata(mock_datetime, patient_mapping):
    mock_datetime.now.return_value = mockdatetime()
    mapping = {
        "id": "resourceId",
        "definition": {"kind": "resource", "derivation": "specialization", "url": "u/r/l"},
        "source": {"id": "sourceId"},
    }
    metadata = transform.build_metadata(mapping)
    assert metadata == {
        "lastUpdated": "now",
        "tag": [
            {"system": f"{ARKHN_TERMINOLOGY_SYSTEM}/source", "code": "sourceId"},
            {"system": f"{ARKHN_TERMINOLOGY_SYSTEM}/resource", "code": "resourceId"},
        ],
    }

    mapping = {
        "id": "resourceId",
        "definition": {"kind": "resource", "derivation": "constraint", "url": "u/r/l"},
        "source": {"id": "sourceId"},
    }
    metadata = transform.build_metadata(mapping)
    assert metadata == {
        "lastUpdated": "now",
        "profile": ["u/r/l"],
        "tag": [
            {"system": f"{ARKHN_TERMINOLOGY_SYSTEM}/source", "code": "sourceId"},
            {"system": f"{ARKHN_TERMINOLOGY_SYSTEM}/resource", "code": "resourceId"},
        ],
    }


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
    path = ["root", "identifier[0]", "value"]
    index = transform.get_position_first_index(path)
    assert index == 1

    path = ["identifier", "value"]
    index = transform.get_position_first_index(path)
    assert index is None


def test_remove_index():
    path = "root.identifier[0]"
    result = transform.remove_index(path)
    assert result == "root.identifier"


def test_get_remove_root_path():
    init_path = "identifier.0.value"
    path = transform.remove_root_path(init_path, 2)
    assert path == "value"
