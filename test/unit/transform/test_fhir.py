import json
import pandas as pd
from unittest import mock

import fhirpipe.transform.fhir as transform

from test.unit import patient_pruned


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_create_fhir_object(_, patient_pruned):
    row = {
        "ADMISSIONS.LANGUAGE": "French",
        "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100092",
        "map_gender_PATIENTS.GENDER": "male",
        "clean_date_PATIENTS.DOB": "2012-12-12",
        "SERVICES.ROW_ID": "2345",
    }
    resource_structure = patient_pruned
    actual = transform.create_fhir_object(row, resource_structure)

    assert actual == {
        "id": actual["id"],
        "identifier": [{"value": "100092"}],
        "resourceType": "Patient",
        "language": "French",
        "gender": "male",
        "birthDate": "2012-12-12",
        "address": [
            {"city": "Paris", "country": "France"},
            {"city": "NY", "state": "NY state", "country": "USA"},
        ],
        "generalPractitioner": [
            {"identifier": {"system": "HealthcareService", "value": "dummy_uri"}}
        ],
    }


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_create_resource(_, patient_pruned):
    rows = pd.DataFrame(
        [
            {
                "ADMISSIONS.LANGUAGE": "French",
                "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100092",
                "map_gender_PATIENTS.GENDER": "male",
                "clean_date_PATIENTS.DOB": "2012-12-12",
                "SERVICES.ROW_ID": "2345",
            },
            {
                "ADMISSIONS.LANGUAGE": "English",
                "select_first_not_empty_PATIENTS.SUBJECT_ID_clean_phone_PATIENTS.ROW_ID_dummy": "100093",
                "map_gender_PATIENTS.GENDER": "female",
                "clean_date_PATIENTS.DOB": "2011-11-11",
                "SERVICES.ROW_ID": "2346",
            },
        ]
    )
    resource_structure = patient_pruned
    actual = transform.create_resource(rows, resource_structure)

    assert actual == [
        {
            "id": actual[0]["id"],
            "identifier": [{"value": "100092"}],
            "resourceType": "Patient",
            "language": "French",
            "gender": "male",
            "birthDate": "2012-12-12",
            "address": [
                {"city": "Paris", "country": "France"},
                {"city": "NY", "state": "NY state", "country": "USA"},
            ],
            "generalPractitioner": [
                {"identifier": {"system": "HealthcareService", "value": "dummy_uri"}}
            ],
        },
        {
            "id": actual[1]["id"],
            "identifier": [{"value": "100093"}],
            "resourceType": "Patient",
            "language": "English",
            "gender": "female",
            "birthDate": "2011-11-11",
            "address": [
                {"city": "Paris", "country": "France"},
                {"city": "NY", "state": "NY state", "country": "USA"},
            ],
            "generalPractitioner": [
                {"identifier": {"system": "HealthcareService", "value": "dummy_uri"}}
            ],
        },
    ]


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_bind_reference(_):
    obj = {
        "identifier": {"value": "dummy_value", "system": "Patient"},
        "other_key": {"other_value"},
    }

    transform.bind_reference(obj)

    assert obj == {
        "identifier": {"value": "dummy_uri", "system": "Patient"},
        "other_key": {"other_value"},
    }
