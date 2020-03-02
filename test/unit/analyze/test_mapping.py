import pytest
from unittest import mock, TestCase

import fhirpipe.analyze.mapping as mapping

from test.unit.conftest import mock_config


@mock.patch("fhirpipe.analyze.mapping.get_mapping_from_file")
@mock.patch("fhirpipe.analyze.mapping.get_mapping_from_graphql")
def test_get_mapping(mock_get_mapping_from_graphql, mock_get_mapping_from_file):

    # When providing file
    mapping.get_mapping(from_file="file", selected_resources=["sel"])
    mock_get_mapping_from_file.assert_called_once_with("file", ["sel"], None)
    mock_get_mapping_from_file.reset_mock()

    mapping.get_mapping(from_file="file")
    mock_get_mapping_from_file.assert_called_once_with("file", None, None)
    mock_get_mapping_from_file.reset_mock()

    # When providing source name
    mapping.get_mapping(selected_source="source", selected_resources=["sel"])
    mock_get_mapping_from_graphql.assert_called_once_with("source", ["sel"], None)
    mock_get_mapping_from_graphql.reset_mock()

    mapping.get_mapping(selected_source="source")
    mock_get_mapping_from_graphql.assert_called_once_with("source", None, None)
    mock_get_mapping_from_graphql.reset_mock()

    # When providing both
    mapping.get_mapping(from_file="file", selected_source="source", selected_resources=["sel"])
    mock_get_mapping_from_file.assert_called_once_with("file", ["sel"], None)
    mock_get_mapping_from_file.reset_mock()

    mapping.get_mapping(from_file="file", selected_source="source")
    mock_get_mapping_from_file.assert_called_once_with("file", None, None)
    mock_get_mapping_from_file.reset_mock()

    # When providing none
    with pytest.raises(ValueError):
        mapping.get_mapping(selected_resources=["sel"])
        mapping.get_mapping()


def test_get_mapping_from_file(exported_source):
    # With selected resources
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file(
            "path", selected_resources=["Patient"], selected_labels=None
        )

    assert [r["definitionId"] for r in resources] == ["Patient"]
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
            "attributes",
        ],
    )

    # Without selected resources
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file(
            "path", selected_resources=None, selected_labels=None
        )

    TestCase().assertCountEqual(
        [r["definitionId"] for r in resources],
        [
            "Patient",
            "Practitioner",
            "EpisodeOfCare",
            "EpisodeOfCare",
            "DiagnosticReport",
            "MedicationRequest",
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
            "attributes",
        ],
    )

    # With selected labels
    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file(
            "path", selected_resources=["EpisodeOfCare"], selected_labels=["wrong_label"]
        )

    assert resources == []

    with mock.patch("builtins.open", mock.mock_open(read_data=exported_source)):
        resources = mapping.get_mapping_from_file(
            "path", selected_resources=["EpisodeOfCare"], selected_labels=["admissions"]
        )

    assert len(resources) == 1


def mock_run_graphql_query(graphql_query, variables=None):
    return {
        "data": {"resources": [{"id": 1, "content": "content1"}, {"id": 2, "content": "content2"}]}
    }


@mock.patch("fhirpipe.analyze.mapping.run_graphql_query", mock_run_graphql_query)
@mock.patch("fhirpipe.analyze.mapping.build_resources_query")
def test_get_mapping_from_graphql(mock_build_resources_query):
    resources = mapping.get_mapping_from_graphql(["chimio"], ["Patient"], None)
    # Need to consume the generator for the assert_called_once_with to work
    resources = list(resources)

    mock_build_resources_query.assert_called_once_with(["chimio"], ["Patient"], None)

    assert resources == [
        {"id": 1, "content": "content1"},
        {"id": 2, "content": "content2"},
    ]


def test_get_primary_key():
    # With owner
    resource_mapping = {
        "primaryKeyOwner": "owner",
        "primaryKeyTable": "table",
        "primaryKeyColumn": "col",
    }
    main_table, column = mapping.get_primary_key(resource_mapping)

    assert main_table == "owner.table"
    assert column == "owner.table.col"

    # Without owner
    resource_mapping = {
        "primaryKeyOwner": "",
        "primaryKeyTable": "table",
        "primaryKeyColumn": "col",
    }
    main_table, column = mapping.get_primary_key(resource_mapping)

    assert main_table == "table"
    assert column == "table.col"

    # Raising error
    resource_mapping = {
        "primaryKeyOwner": "",
        "primaryKeyTable": "",
        "primaryKeyColumn": "col",
        "definitionId": "fhirtype",
    }
    with pytest.raises(
        ValueError, match="You need to provide a primary key table and column in the mapping"
    ):
        main_table, column = mapping.get_primary_key(resource_mapping)


def mock_api_get_maps(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "https://url/api/ConceptMap/123":
        return MockResponse(
            {
                "group": [
                    {
                        "element": [
                            {"code": "1", "target": [{"code": "A"}]},
                            {"code": "2", "target": [{"code": "B"}]},
                            {"code": "3", "target": [{"code": "C"}]},
                        ],
                    }
                ],
                "resourceType": "ConceptMap",
                "title": "cm123",
            },
            200,
        )
    elif args[0] == "https://url/api/ConceptMap/456":
        return MockResponse(
            {
                "group": [
                    {
                        "element": [
                            {"code": "4", "target": [{"code": "D"}]},
                            {"code": "5", "target": [{"code": "E"}]},
                            {"code": "6", "target": [{"code": "F"}]},
                        ],
                    }
                ],
                "resourceType": "ConceptMap",
                "title": "cm456",
            },
            200,
        )
    elif args[0] == "https://url/api/ConceptMap/789":
        return MockResponse(
            {
                "group": [
                    {
                        "element": [
                            {"code": "7", "target": [{"code": "G"}]},
                            {"code": "8", "target": [{"code": "H"}]},
                            {"code": "9", "target": [{"code": "I"}]},
                        ],
                    }
                ],
                "resourceType": "ConceptMap",
                "title": "cm789",
            },
            200,
        )
    return MockResponse(None, 404)


@mock.patch("fhirpipe.analyze.mapping.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.mapping.requests.get", mock_api_get_maps)
def test_get_dict_concept_maps():
    resource_mapping = {
        "attributes": [
            {"inputs": [{"conceptMapId": "123"}, {"conceptMapId": "456"}]},
            {"inputs": [{"conceptMapId": "789"}]},
        ]
    }
    dicts = mapping.get_dict_concept_maps(resource_mapping)

    assert dicts == {
        "123": ("cm123", {"1": "A", "2": "B", "3": "C"}),
        "456": ("cm456", {"4": "D", "5": "E", "6": "F"}),
        "789": ("cm789", {"7": "G", "8": "H", "9": "I"}),
    }


@mock.patch("fhirpipe.analyze.mapping.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.mapping.requests.get", mock_api_get_maps)
def test_fetch_concept_map():
    concept_map = mapping.fetch_concept_map("123")

    assert concept_map == {
        "group": [
            {
                "element": [
                    {"code": "1", "target": [{"code": "A"}]},
                    {"code": "2", "target": [{"code": "B"}]},
                    {"code": "3", "target": [{"code": "C"}]},
                ],
            }
        ],
        "resourceType": "ConceptMap",
        "title": "cm123",
    }


def test_concept_map_to_dict():
    concept_map = {
        "sourceUri": "sourceUri",
        "targetUri": "targetUri",
        "group": [
            {
                "source": "src",
                "target": "trgt",
                "element": [
                    {"code": "src_code", "target": [{"code": "trgt_code"}, {"code": "not_used"}]},
                    {"code": "code1", "target": [{"code": "code2"}]},
                ],
            },
            {
                "source": "sys1",
                "target": "sys2",
                "element": [
                    {"code": "11", "target": [{"code": "12"}]},
                    {"code": "21", "target": [{"code": "22"}]},
                    {"code": "31", "target": [{"code": "32"}]},
                ],
            },
        ],
    }

    dict_map = mapping.concept_map_to_dict(concept_map)

    assert dict_map == {
        "src_code": "trgt_code",
        "code1": "code2",
        "11": "12",
        "21": "22",
        "31": "32",
    }


def test_find_cols_joins_maps_scripts(patient_mapping):
    fhir_resource = patient_mapping

    cols, joins, cleaning, concept_maps, merging = mapping.find_cols_joins_maps_scripts(
        fhir_resource
    )

    assert cols == {
        "PATIENTS.GENDER",
        "PATIENTS.DOB",
        "admissions.marital_status",
        "patients.row_id",
        "admissions.hospital_expire_flag",
        "patients.dod",
    }
    assert joins == {("patients.subject_id", "admissions.subject_id")}
    assert cleaning == {
        "map_gender": ["PATIENTS.GENDER"],
        "clean_date": ["PATIENTS.DOB", "patients.dod"],
        "map_marital_status": ["admissions.marital_status"],
        "binary_to_bool_1": ["admissions.hospital_expire_flag"],
    }
    assert concept_maps == {}
    assert merging == []


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


# TODO uncomment and reimplement test when referencing enabled
# def test_find_reference_attributes(patient_mapping):
#     # TODO this test is a bit light
#     fhir_resource = patient_mapping

#     actual = mapping.find_reference_attributes(fhir_resource)

#     expected = [("generalPractitioner",)]

#     assert actual == expected
