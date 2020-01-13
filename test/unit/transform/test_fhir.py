import json
import pandas as pd
from unittest import mock

import fhirpipe.transform.fhir as transform

from test.unit import resource_pruned


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_create_fhir_object(_, resource_pruned):
    row = {
        "PATIENT.SUBJECT_ID": "100092",
        "clean_date_PATIENTS.DOB": "2012-12-12",
        "map_gender_PATIENTS.GENDER": "MALE",
        "ADMISSIONS.SUBJECT_ID": "100092",
        "ADMISSIONS.LANGUAGE": "French",
        "select_first_not_empty_CAREGIVERS.DESCRIPTION_clean_date_PATIENTS.DOD_": "2070-10-10",
    }
    resource_structure = resource_pruned
    pk = "PATIENT.SUBJECT_ID"
    actual = transform.create_fhir_object(row, resource_structure, pk)

    assert actual == {
        "id": "100092",
        "resourceType": "Patient",
        "name": [[{"family": "family name"}]],
        "language": "French",
        "gender": "MALE",
        "birthDate": "2012-12-12",
        "deceasedDateTime": "2070-10-10",
        "address": [
            [{"city": "Paris", "country": "France"}],
            [{"city": "NY", "country": "USA"}],
        ],
        "managingOrganization": {
            "identifier": {"system": "Patient", "value": "dummy_uri"}
        },
    }


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_create_resource(_, resource_pruned):
    rows = pd.DataFrame(
        [
            {
                "PATIENT.SUBJECT_ID": "100092",
                "clean_date_PATIENTS.DOB": "2012-12-12",
                "map_gender_PATIENTS.GENDER": "MALE",
                "ADMISSIONS.SUBJECT_ID": "100092",
                "ADMISSIONS.LANGUAGE": "French",
                "select_first_not_empty_CAREGIVERS.DESCRIPTION_clean_date_PATIENTS.DOD_": "2070-10-10",
            },
            {
                "PATIENT.SUBJECT_ID": "100093",
                "clean_date_PATIENTS.DOB": "2012-11-11",
                "map_gender_PATIENTS.GENDER": "FEMALE",
                "ADMISSIONS.SUBJECT_ID": "100093",
                "ADMISSIONS.LANGUAGE": "English",
                "select_first_not_empty_CAREGIVERS.DESCRIPTION_clean_date_PATIENTS.DOD_": "2075-10-10",
            },
        ]
    )
    resource_structure = resource_pruned
    pk = "PATIENT.SUBJECT_ID"
    actual = transform.create_resource(rows, resource_structure, pk)

    assert actual == [
        {
            "id": "100092",
            "resourceType": "Patient",
            "name": [[{"family": "family name"}]],
            "language": "French",
            "gender": "MALE",
            "birthDate": "2012-12-12",
            "deceasedDateTime": "2070-10-10",
            "address": [
                [{"city": "Paris", "country": "France"}],
                [{"city": "NY", "country": "USA"}],
            ],
            "managingOrganization": {
                "identifier": {"system": "Patient", "value": "dummy_uri"}
            },
        },
        {
            "id": "100093",
            "resourceType": "Patient",
            "name": [[{"family": "family name"}]],
            "language": "English",
            "gender": "FEMALE",
            "birthDate": "2012-11-11",
            "deceasedDateTime": "2075-10-10",
            "address": [
                [{"city": "Paris", "country": "France"}],
                [{"city": "NY", "country": "USA"}],
            ],
            "managingOrganization": {
                "identifier": {"system": "Patient", "value": "dummy_uri"}
            },
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
