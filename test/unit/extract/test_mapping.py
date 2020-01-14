import os
import json
import pytest
from unittest import mock

import fhirpipe.extract.mapping as mapping
import fhirpipe.extract.graphql as gql

from test.unit import exported_source, gql_response, resource_pruned


@mock.patch("fhirpipe.extract.mapping.get_mapping_from_file")
@mock.patch("fhirpipe.extract.mapping.get_mapping_from_graphql")
def test_get_mapping(mock_get_mapping_from_graphql, mock_get_mapping_from_file):

    # When providing file
    mapping.get_mapping(from_file="file", selected_resources=["sel"])
    mock_get_mapping_from_file.assert_called_once_with("file", ["sel"])
    mock_get_mapping_from_file.reset_mock()

    mapping.get_mapping(from_file="file")
    mock_get_mapping_from_file.assert_called_once_with("file", None)
    mock_get_mapping_from_file.reset_mock()

    # When providing source name
    mapping.get_mapping(source_name="source", selected_resources=["sel"])
    mock_get_mapping_from_graphql.assert_called_once_with("source", ["sel"])
    mock_get_mapping_from_graphql.reset_mock()

    mapping.get_mapping(source_name="source")
    mock_get_mapping_from_graphql.assert_called_once_with("source", None)
    mock_get_mapping_from_graphql.reset_mock()

    # When providing both
    mapping.get_mapping(
        from_file="file", source_name="source", selected_resources=["sel"]
    )
    mock_get_mapping_from_file.assert_called_once_with("file", ["sel"])
    mock_get_mapping_from_file.reset_mock()

    mapping.get_mapping(from_file="file", source_name="source")
    mock_get_mapping_from_file.assert_called_once_with("file", None)
    mock_get_mapping_from_file.reset_mock()

    # When providing none
    with pytest.raises(ValueError):
        mapping.get_mapping(selected_resources=["sel"])
        mapping.get_mapping()


def test_get_mapping_from_file(exported_source, gql_response):
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file("path", selected_resources=None)

    assert resources == [gql_response]


def mock_run_graphql_query(graphql_query, variables=None):
    if graphql_query == gql.sources_query:
        return {
            "data": {
                "sources": [
                    {
                        "id": 123,
                        "name": "aphp",
                        "resources": [
                            {"id": 1, "fhirType": "Patient"},
                            {"id": 2, "fhirType": "Observation"},
                        ],
                    },
                    {
                        "id": 456,
                        "name": "chimio",
                        "resources": [
                            {"id": 3, "fhirType": "Practitioner"},
                            {"id": 4, "fhirType": "Medication"},
                        ],
                    },
                ]
            }
        }

    elif graphql_query == gql.resource_query:

        if variables["resourceId"] == 1:
            return {"data": {"resource": {"id": 1, "content": "content1",}}}

        elif variables["resourceId"] == 2:
            return {"data": {"resource": {"id": 2, "content": "content2",}}}


@mock.patch("fhirpipe.extract.mapping.run_graphql_query", mock_run_graphql_query)
def test_get_mapping_from_graphql():
    # With selected resources
    resources = mapping.get_mapping_from_graphql("aphp", ["Patient"])

    assert list(resources) == [{"id": 1, "content": "content1"}]

    # Without selected resources
    resources = mapping.get_mapping_from_graphql("aphp", None)

    assert list(resources) == [
        {"id": 1, "content": "content1"},
        {"id": 2, "content": "content2"},
    ]


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
            (["CAREGIVERS.DESCRIPTION", "clean_date_PATIENTS.DOD"], [],)
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
