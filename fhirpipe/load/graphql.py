import json
import os
import requests

from fhirpipe.config import Config


config = Config("graphql")
SERVER = config.server
HEADERS = {
    "content-type": "application/json",
    "Authorization": f"Bearer {config.token}",
}


source_info_query = """
query {
    sourceInfo(sourceName: $sourceName) {
        id
        name
    }
}
"""

available_resources_query = """
query {
    availableResources(sourceId: $sourceId) {
        id
        name
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

query {
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
    )
    return query


def run_graphql_query(graphql_query, variables=None):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """

    request = requests.post(
        SERVER,
        headers=HEADERS,
        json={"query": graphql_query, "variables": variables, "operationName": None},
    )

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with returning code {}.".format(request.status_code)
        )


def get_fhir_resource(source_name, resource_name, from_file=None):
    """
    Formats GraphQL query with given arguments
    before calling api endpoint.

    Args:
        database (str): name of the database or software for which the mapping rules are intended
        resource (str): name of Fhir resource we want to fill with the mapping rules
        from_file (str or None): optional file name to load mapping rules from a file
    """

    if from_file is not None:
        path = from_file
        real_path = "/".join(
            os.path.abspath(__file__).split("/")[:-1] + path.split("/")
        )

        with open(real_path) as json_file:
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
        # Get Source id from Source name
        source = run_graphql_query(source_info_query, variables={sourceName: source_name})
        source_id = source["data"]["sourceInfo"]["id"]

        # Check that Resource exists for given Source
        available_resources = run_graphql_query(available_resources_query, variables={sourceId: source_id})
        assert(
            resource_name in list(map(lambda x: x["name"], available_resources["data"]["availableResources"]))
        ), f"Resource {resource_name} doesn't exist for Source {source_name}"

        # Deduce Resource id from Resource name
        resource_id = list(filter(lambda x: x["name"] == resource_name, available_resources["data"]["availableResources"]))[0]["id"]

        # Get Resource mapping
        resource = run_graphql_query(resource_query, variables={resourceId: resource_id})

        return resource["data"]["resource"]
