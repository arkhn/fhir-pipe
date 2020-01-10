import requests

import fhirpipe


sources_query = """
query {
    sources {
        id
        name
        resources {
          id
          fhirType
        }
    }
}
"""

resource_query = """
fragment entireColumn on Column {
    id
    owner
    table
    column
    joins {
        id
        tables {
            id
            owner
            table
            column
        }
    }
}

fragment entireInput on Input {
    id
    sqlValue {
        ...entireColumn
    }
    script
    staticValue
}

fragment a on Attribute {
    id
    name
    fhirType
    mergingScript
    inputs {
        ...entireInput
    }
}

query($resourceId: ID!) {
    resource(resourceId: $resourceId) {
        id
        fhirType
        primaryKeyOwner
        primaryKeyTable
        primaryKeyColumn
        attributes {
            ...a
            children {
                ...a
                children {
                    ...a
                    children {
                        ...a
                        children {
                            ...a
                            children {
                                ...a
                                children {
                                    ...a
                                    children {
                                        ...a
                                        children {
                                            ...a
                                            children {
                                                ...a
                                                children {
                                                    ...a
                                                    children {
                                                        ...a
                                                        children {
                                                            ...a
                                                            children {
                                                                ...a
                                                                children {
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
        "Authorization": f"Bearer {fhirpipe.global_config['graphql']['token']}",
    }


def run_graphql_query(graphql_query, variables=None):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """
    request = requests.post(
        fhirpipe.global_config["graphql"]["server"],
        headers=get_headers(),
        json={"query": graphql_query, "variables": variables},
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with returning code {}\n{}.".format(
                request.status_code, request.reason
            )
        )
