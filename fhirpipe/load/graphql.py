import json
import os
import requests

import fhirpipe


def get_headers():
    return {
        "content-type": "application/json",
        "Authorization": f"Bearer {fhirpipe.global_config.graphql.token}",
    }


source_info_query = """
query($sourceName: String!) {
    sourceInfo(sourceName: $sourceName) {
        id
        name
    }
}
"""

available_resources_query = """
query($sourceId: ID!) {
    availableResources(sourceId: $sourceId) {
        id
        fhirType
        label
    }
}
"""

resource_query = """
fragment entireJoin on Join {
    id
    sourceOwner
    sourceTable
    sourceColumn
    targetOwner
    targetTable
    targetColumn
}

fragment entireInputColumn on InputColumn {
    id
    owner
    table
    column
    script
    staticValue
    joins {
        ...entireJoin
    }
}

fragment a on Attribute {
    id
    comment
    name
    mergingScript
    isProfile
    type
    inputColumns {
        ...entireInputColumn
    }
}

query($resourceId: ID!) {
    resource(where: {id: $resourceId}) {
        id
        name
        attributes {
            ...a
            attributes {
                ...a
                attributes {
                    ...a
                    attributes {
                        ...a
                        attributes {
                            ...a
                            attributes {
                                ...a
                                attributes {
                                    ...a
                                    attributes {
                                        ...a
                                        attributes {
                                            ...a
                                            attributes {
                                                ...a
                                                attributes {
                                                    ...a
                                                    attributes {
                                                        ...a
                                                        attributes {
                                                            ...a
                                                            attributes {
                                                                ...a
                                                                attributes {
                                                                    ...a
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
"""


def run_graphql_query(graphql_query, variables=None):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """
    request = requests.post(
        fhirpipe.global_config.graphql.server, headers=get_headers(), json={
            "query": graphql_query, "variables": variables}
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with returning code {}\n{}.".format(
                request.status_code, request.reason
            )
        )


def get_fhir_resource(source_name, resource_name, from_file=None):
    """
    Formats GraphQL query with given arguments
    before calling api endpoint.

    Args:
        source_name (str): name of the database or software for which the mapping rules are intended
        resource_name (str): name of Fhir resource we want to fill with the mapping rules
        from_file (str or None): optional file name to load mapping rules from a file
    """

    if from_file is not None:
        path = from_file
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)

        with open(path) as json_file:
            resources = json.load(json_file)
        source_json = resources["data"]["database"]

        assert (
            source_json["name"] == source_name
        ), f"Source {source_name} is not in the graphql json resource"

        for resource_json in source_json["resources"]:
            if resource_json["name"] == resource_name:
                return resource_json

        raise FileNotFoundError(
            f"Resource {resource_name} not found in the graphql json resource"
        )
    else:
        available_resources = get_available_resources(source_name)
        assert resource_name in list(
            map(lambda x: x["fhirType"], available_resources["data"]["availableResources"])
        ), f"Resource {resource_name} doesn't exist for Source {source_name}"

        # Deduce Resource id from Resource name
        resource_id = list(
            filter(
                lambda x: x["fhirType"] == resource_name,
                available_resources["data"]["availableResources"],
            )
        )[0]["id"]  # TODO: multiple resources can exists for a given fhirType

        # Get Resource mapping
        resource = run_graphql_query(
            resource_query, variables={"resourceId": resource_id}
        )

        return resource["data"]["resource"]


def get_available_resources(source_name, from_file=None):
    """
    Get all available resources from a pyrog mapping.
    The mapping may either come from a static file or from
    a pyrog graphql API.

    Args:
        source_name: name of the project (eg: Mimic)
        from_file (optional): path to the static file to mock
                              the pyrog API response.
    """
    if from_file:
        path = from_file
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)

        with open(path) as json_file:
            resources = json.load(json_file)
        source_json = resources["data"]["database"]

        return source_json["resources"]

    else:
        # Get Source id from Source name
        source = run_graphql_query(
            source_info_query, variables={"sourceName": source_name}
        )
        source_id = source["data"]["sourceInfo"]["id"]

        # Check that Resource exists for given Source
        available_resources = run_graphql_query(
            available_resources_query, variables={"sourceId": source_id}
        )
        return available_resources["data"]["availableResources"]
