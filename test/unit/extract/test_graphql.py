from unittest import mock
from pytest import raises

from test.unit import mock_config
import fhirpipe.extract.graphql as gql


def test_build_resources_query():
    # With selected source
    query = gql.build_resources_query(selected_source="mimic")

    assert (
        """source: {
                name: { equals: "mimic" }
            }"""
        in query
    )

    # With selected resources
    query = gql.build_resources_query(selected_resources=["Patient", "Observation"])

    assert (
        """definition: {
                type: { in: ["Patient", "Observation"] }
            }"""
        in query
    )

    # With selected source
    query = gql.build_resources_query(selected_labels=["label"])

    assert 'label: { in: ["label"] }' in query

    # With all arguments
    query = gql.build_resources_query(
        selected_source="mimic",
        selected_resources=["Patient", "Observation"],
        selected_labels=["label"],
    )

    assert (
        """source: {
                name: { equals: "mimic" }
            }
            definition: {
                type: { in: ["Patient", "Observation"] }
            }
            label: { in: ["label"] }"""
        in query
    )


@mock.patch("fhirpipe.extract.graphql.fhirpipe.global_config", mock_config)
def test_get_headers():
    header = gql.get_headers()

    assert header == {
        "content-type": "application/json",
        "Authorization": "Bearer gql_token",
    }


@mock.patch("fhirpipe.extract.graphql.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.extract.graphql.requests.post")
def test_run_graphql_query(mock_post):
    mock_post.return_value = mock.MagicMock()

    # No error
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"data": "successful query"}

    response = gql.run_graphql_query("query")
    assert response == {"data": "successful query"}

    # Request error
    mock_post.return_value.status_code = 400
    mock_post.return_value.reason = "reason"

    with raises(Exception, match=f"Query failed with returning code 400\nreason."):
        gql.run_graphql_query("query")

    # GraphQL error
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"data": None, "errors": "error message"}

    with raises(Exception, match="GraphQL query failed with errors: error message."):
        gql.run_graphql_query("query")
