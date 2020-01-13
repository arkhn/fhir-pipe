import os
import json
from unittest import mock

import fhirpipe.extract.mapping as mapping

from test.unit import exported_source, gql_response, resource_pruned


def test_get_mapping_from_file(exported_source):
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file("path", selected_resources=None)

    assert [r["fhirType"] for r in resources] == [
        "Patient",
    ]


# def test_get_mapping_from_graphql():
#     pass


def test_prune_fhir_resource(gql_response, resource_pruned):
    actual = mapping.prune_fhir_resource(gql_response)

    assert actual == resource_pruned


def test_find_cols_joins_and_scripts(resource_pruned):
    fhir_resource = resource_pruned

    cols, joins, cleaning, merging = mapping.find_cols_joins_and_scripts(fhir_resource)
    print(cols, joins, cleaning, merging)

    assert cols == {
        "PATIENTS.DOB",
        "PATIENTS.DOD",
        "PATIENTS.GENDER",
        "ADMISSIONS.SUBJECT_ID",
        "ADMISSIONS.LANGUAGE",
        "CAREGIVERS.DESCRIPTION",
    }
    assert joins == {
        ("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID"),
        ("PATIENTS.SUBJECT_ID", "CAREGIVERS.ROW_ID"),
    }
    assert cleaning == {
        "map_gender": ["PATIENTS.GENDER"],
        "clean_date": ["PATIENTS.DOB", "PATIENTS.DOD"],
    }
    assert merging == {
        "select_first_not_empty": [
            (
                ["CAREGIVERS.DESCRIPTION", "clean_date_PATIENTS.DOD"],
                [],
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
