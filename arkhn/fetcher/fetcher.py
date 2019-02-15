import requests

from arkhn.config import Config


CONFIG = Config("graphql")
SERVER = CONFIG.server
HEADERS = {
    "content-type": "application/json",
}
QUERY = """
fragment entireJoin on Join {{
    id
    sourceOwner
    sourceTable
    sourceColumn
    targetOwner
    targetTable
    targetColumn
}}

fragment entireInputColumn on InputColumn {{
    id
    owner
    table
    column
    script
    staticValue
    joins {{
        ...entireJoin
    }}
}}

fragment a on Attribute {{
    id
    comment
    name
    mergingScript
    isProfile
    type
    inputColumns {{
        ...entireInputColumn
    }}
}}

query {{
    getResource (database: "{0}", resource: "{1}") {{
        id
        name
        attributes {{
            ...a
            attributes {{
                ...a
                attributes {{
                    ...a
                    attributes {{
                        ...a
                        attributes {{
                            ...a
                            attributes {{
                                ...a
                                attributes {{
                                    ...a
                                    attributes {{
                                        ...a
                                        attributes {{
                                            ...a
                                            attributes {{
                                                ...a
                                                attributes {{
                                                    ...a
                                                    attributes {{
                                                        ...a
                                                        attributes {{
                                                            ...a
                                                            attributes {{
                                                                ...a
                                                                attributes {{
                                                                    ...a
                                                                }}
                                                            }}
                                                        }}
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
"""


def run_query(query):
    """
    This function queries a GraphQL endpoint
    and returns a json parsed response.
    """

    request = requests.post(
        SERVER,
        headers=HEADERS,
        json={
            'query': query,
            'variables': None,
            'operationName': None,
        }
    )

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed with returning code {}.".format(request.status_code))


def get_fhir_resource(database, resource):
    """
    Formats GraphQL query with given arguments
    before calling api endpoint.
    """

    return run_query(QUERY.format(database, resource))
