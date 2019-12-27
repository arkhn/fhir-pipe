import json
import os
import requests

import fhirpipe


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


def get_headers():
    return {
        "content-type": "application/json",
        "Authorization": f"Bearer {fhirpipe.global_config.graphql.token}",
    }


def run_graphql_query(graphql_query, variables=None):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """
    request = requests.post(
        fhirpipe.global_config.graphql.server,
        headers=get_headers(),
        json={"query": graphql_query, "variables": variables},
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with returning code {}\n{}.".format(request.status_code, request.reason)
        )