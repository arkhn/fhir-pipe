import os
import json
import pytest
from unittest import mock, TestCase

import fhirpipe.extract.mapping as mapping
import fhirpipe.extract.graphql as gql

from test.unit import exported_source, patient_pruned


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


def test_get_mapping_from_file(exported_source):
    # With selected resources
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file("path", selected_resources="Patient")

    assert len(resources) == 1
    assert [r["fhirType"] for r in resources] == ["Patient"]
    TestCase().assertCountEqual(
        resources[0].keys(),
        [
            "fhirType",
            "id",
            "label",
            "profile",
            "primaryKeyOwner",
            "primaryKeyTable",
            "primaryKeyColumn",
            "createdAt",
            "updatedAt",
            "attributes",
        ],
    )

    # Without selected resources
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file("path", selected_resources=None)

    assert len(resources) == 2
    assert [r["fhirType"] for r in resources] == ["Patient", "HealthcareService"]
    TestCase().assertCountEqual(
        resources[0].keys(),
        [
            "fhirType",
            "id",
            "label",
            "profile",
            "primaryKeyOwner",
            "primaryKeyTable",
            "primaryKeyColumn",
            "createdAt",
            "updatedAt",
            "attributes",
        ],
    )


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
            return {"data": {"resource": {"id": 1, "content": "content1"}}}

        elif variables["resourceId"] == 2:
            return {"data": {"resource": {"id": 2, "content": "content2"}}}


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


def test_prune_fhir_resource(exported_source, patient_pruned):
    resource = json.loads(exported_source)[0]
    actual = mapping.prune_fhir_resource(resource)

    # with open("test/fixtures/patient_pruned.json", "w") as fp:
    #     json.dump(actual, fp, indent=2, separators=(",", ": "))

    assert actual == patient_pruned


def test_find_cols_joins_and_scripts(patient_pruned):
    fhir_resource = patient_pruned

    cols, joins, cleaning, merging = mapping.find_cols_joins_and_scripts(fhir_resource)
    print(cols, joins, cleaning, merging)

    assert cols == {
        "PATIENTS.ROW_ID",
        "PATIENTS.SUBJECT_ID",
        "PATIENTS.DOB",
        "PATIENTS.GENDER",
        "ADMISSIONS.LANGUAGE",
        "SERVICES.ROW_ID",
    }
    assert joins == {
        ("PATIENTS.SUBJECT_ID", "ADMISSIONS.SUBJECT_ID"),
        ("PATIENTS.SUBJECT_ID", "SERVICES.SUBJECT_ID"),
    }
    assert cleaning == {
        "clean_phone": ["PATIENTS.ROW_ID"],
        "map_gender": ["PATIENTS.GENDER"],
        "make_title": ["ADMISSIONS.LANGUAGE"],
        "clean_date": ["PATIENTS.DOB"],
    }
    assert merging == {
        "select_first_not_empty": [
            (["PATIENTS.SUBJECT_ID", "clean_phone_PATIENTS.ROW_ID"], ["dummy"])
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


def test_find_reference_attributes(patient_pruned):
    # TODO this test is a bit light
    fhir_resource = patient_pruned

    actual = mapping.find_reference_attributes(fhir_resource)

    expected = [("generalPractitioner",)]

    assert actual == expected
