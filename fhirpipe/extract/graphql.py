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
          label
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
    response = requests.post(
        fhirpipe.global_config["graphql"]["server"],
        headers=get_headers(),
        json={"query": graphql_query, "variables": variables},
    )
    if response.status_code != 200:
        raise Exception(
            f"Query failed with returning code {response.status_code}\n{response.reason}."
        )

    json_response = response.json()
    if "errors" in json_response:
        raise Exception(f"GraphQL query failed with errors: {json_response['errors']}.")

    return json_response
