import requests

from fhirpipe.config import Config


config = Config("graphql")
SERVER = config.server
HEADERS = {
    "content-type": "application/json",
    "Authorization": f"Bearer {config.token}",
}


def get_query(database, resource):
    query = (
        """
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
        getResource (database: """
        + database
        + """, resource: """
        + resource
        + """) {
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


def run_query(query):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """

    request = requests.post(
        SERVER,
        headers=HEADERS,
        json={"query": query, "variables": None, "operationName": None},
    )

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed with returning code {}.".format(request.status_code)
        )


def get_fhir_resource(database, resource):
    """
    Formats GraphQL query with given arguments
    before calling api endpoint.
    """

    response = run_query(get_query(database, resource))
    response = response["data"]["getResource"]

    return response
