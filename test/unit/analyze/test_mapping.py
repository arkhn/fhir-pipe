import pytest
from unittest import mock, TestCase

import fhirpipe.analyze.mapping as mapping
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin

from test.unit.conftest import mock_config


@mock.patch("fhirpipe.extract.graphql.PyrogClient")
@mock.patch("fhirpipe.analyze.mapping.get_mapping_from_file")
@mock.patch("fhirpipe.analyze.mapping.get_mapping_from_graphql")
@mock.patch("fhirpipe.extract.graphql.fhirpipe.global_config", mock_config)
def test_get_mapping(mock_get_mapping_from_graphql, mock_get_mapping_from_file, mock_pyrog_client):

    # When providing file
    mapping.get_mapping(from_file="file")
    mock_get_mapping_from_file.assert_called_once_with("file")
    mock_get_mapping_from_file.reset_mock()

    mapping.get_mapping(from_file="file", resource_ids=["sel"])
    mock_get_mapping_from_file.assert_called_once_with("file")
    mock_get_mapping_from_file.reset_mock()

    # When providing resource ids
    mapping.get_mapping(resource_ids=["sel"], pyrog_client=mock_pyrog_client())
    mock_get_mapping_from_graphql.assert_called_once_with(["sel"], mock_pyrog_client())
    mock_get_mapping_from_graphql.reset_mock()

    # When providing none
    with pytest.raises(ValueError):
        mapping.get_mapping()


def test_get_mapping_from_file(exported_source):
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file("path")

    TestCase().assertCountEqual(
        [r["definitionId"] for r in resources],
        [
            "Patient",
            "Practitioner",
            "EpisodeOfCare",
            "EpisodeOfCare",
            "DiagnosticReport",
            "MedicationRequest",
            "PractitionerRole",
        ],
    )
    TestCase().assertCountEqual(
        resources[0].keys(),
        [
            "id",
            "label",
            "primaryKeyOwner",
            "primaryKeyTable",
            "primaryKeyColumn",
            "updatedAt",
            "createdAt",
            "definitionId",
            "definition",
            "source",
            "filters",
            "attributes",
        ],
    )


def mock_run_graphql_query(graphql_query, variables=None):
    return {
        "data": {"resources": [{"id": 1, "content": "content1"}, {"id": 2, "content": "content2"}]}
    }


@mock.patch("fhirpipe.extract.graphql.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.extract.graphql.PyrogClient")
@mock.patch("fhirpipe.extract.graphql.PyrogClient.run_graphql_query")
def test_get_mapping_from_graphql(mock_run_graphql_query, mock_pyrog_client):
    # Mock pyrog_client
    pyrog_client = mock_pyrog_client()

    pyrog_client.get_resource_from_id.side_effect = [
        {"id": 1, "content": "content1"},
        {"id": 2, "content": "content2"},
    ]

    resources = mapping.get_mapping_from_graphql(
        ["resource_id_1", "resource_id_2"], pyrog_client=pyrog_client
    )
    # Need to consume the generator for the assert_called_once_with to work
    resources = list(resources)

    assert pyrog_client.get_resource_from_id.call_count == 2

    assert resources == [
        {"id": 1, "content": "content1"},
        {"id": 2, "content": "content2"},
    ]


def test_build_squash_rules():
    cols = [
        "ADMISSIONS.LANGUAGE",
        "PATIENTS.DOD",
        "PATIENTS.SUBJECT_ID",
    ]  # NOTE: I use a list instead of a set to keep the order of elements
    joins = {SqlJoin(SqlColumn("PATIENTS", "SUBJECT_ID"), SqlColumn("ADMISSIONS", "SUBJECT_ID"))}
    table = "PATIENTS"

    actual = mapping.build_squash_rules(cols, joins, table)

    assert actual == ["PATIENTS", [["ADMISSIONS", []]]]
