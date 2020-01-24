import json
import pandas as pd
import pytest
from unittest import mock

import fhirpipe.transform.fhir as transform

from test.unit import patient_pruned
from test.unit.load import mock_mongo_client


def test_create_fhir_object(patient_pruned):
    row = ["Engl", "100092", "male", "2012-12-12", "2345"]
    resource_structure = patient_pruned
    actual = transform.create_fhir_object(row, resource_structure)

    assert actual == {
        "id": actual["id"],
        "identifier": [{"value": "100092"}],
        "resourceType": "Patient",
        "language": "Engl",
        "gender": "male",
        "birthDate": "2012-12-12",
        "address": [
            {"city": "Paris", "country": "France"},
            {"city": "NY", "state": "NY state", "country": "USA"},
        ],
        "generalPractitioner": [
            {"identifier": {"system": "HealthcareService", "value": "2345"}}
        ],
    }


def test_create_resource(patient_pruned):
    rows = pd.DataFrame(
        [
            ["Engl", "100092", "male", "2012-12-12", "2345"],
            ["Fren", "100093", "female", "2011-11-112", "2346"],
        ]
    )
    resource_structure = patient_pruned
    actual = transform.create_resource(rows, resource_structure)

    assert actual == [
        {
            "id": actual[0]["id"],
            "identifier": [{"value": "100092"}],
            "resourceType": "Patient",
            "language": "Engl",
            "gender": "male",
            "birthDate": "2012-12-12",
            "address": [
                {"city": "Paris", "country": "France"},
                {"city": "NY", "state": "NY state", "country": "USA"},
            ],
            "generalPractitioner": [
                {"identifier": {"system": "HealthcareService", "value": "2345"}}
            ],
        },
        {
            "id": actual[1]["id"],
            "identifier": [{"value": "100093"}],
            "resourceType": "Patient",
            "language": "Fren",
            "gender": "female",
            "birthDate": "2011-11-11",
            "address": [
                {"city": "Paris", "country": "France"},
                {"city": "NY", "state": "NY state", "country": "USA"},
            ],
            "generalPractitioner": [
                {"identifier": {"system": "HealthcareService", "value": "2346"}}
            ],
        },
    ]


# def test_min_length_leave():
#     in_dict = {"a": [1, 2, 3], "b": {"c": [1, 2, 3], "d": 1}}
#     res = transform.min_length_leave(in_dict)
#
#     assert res == 3
#
#     # Should raise an exception
#     in_dict = {"a": [1, 2, 3], "b": {"c": [1, 2], "d": 1}}
#     with pytest.raises(Exception, match="Inconsistant lengths in child leaves."):
#         res = transform.min_length_leave(in_dict)
#
#
# def test_dl_2_ld():
#     in_dict = {"a": [1, 2, 3], "b": {"c": [1, 2, 3], "d": 1}}
#     actual = transform.dl_2_ld(in_dict, 3)
#
#     expected = [
#         {"a": 1, "b": {"c": 1, "d": 1}},
#         {"a": 2, "b": {"c": 2, "d": 1}},
#         {"a": 3, "b": {"c": 3, "d": 1}},
#     ]
#
#     assert actual == expected
#
#
# def test_select_index_in_dl():
#     in_dict = {"a": [1, 2, 3], "b": {"c": [1, 2, 3], "d": 1}}
#     transform.select_index_in_dl(in_dict, 1)
#
#     expected = {"a": 2, "b": {"c": 2, "d": 1}}
#
#     assert in_dict == expected
#
#
# def unlist_dict():
#     in_dict = {"a": [1, 1], "b": {"c": [1], "d": 1}}
#     unlist_dict(in_dict)
#
#     expected = {"a": 1, "b": {"c": 1, "d": 1}}
#
#     assert in_dict == expected
#
#     # Should raise an exception
#     in_dict = {"a": [1, 2], "b": {"c": [1], "d": 1}}
#     with pytest.raises(
#         Exception,
#         match="You cannot create a non-list attribute with a list of different values.",
#     ):
#         res = transform.min_length_leave(in_dict)
#
