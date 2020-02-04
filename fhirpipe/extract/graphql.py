import requests

import fhirpipe
from fhirpipe.errors import OperationOutcome


credential_query = """
query credential($credentialId: ID!) {
    credential(credentialId: $credentialId) {
        model
        host
        port
        database
        login
        password
    }
}
"""


def build_resources_query(selected_sources=None, selected_resources=None, selected_labels=None):
    """ Builds a graphql query fetching all the resources needed.

    Note that the .replace("'", '"') is needed because the graphql needs to have
    strings delimited by double quotes.
    """
    source_filter = (
        """source: {
                name: { in: %s }
            }"""
        % selected_sources
        if selected_sources
        else ""
    )
    resource_filter = "fhirType: { in: %s }" % selected_resources if selected_resources else ""
    label_filter = "label: { in: %s }" % selected_labels if selected_labels else ""

    return (
        """fragment entireColumn on Column {
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

query {
    resources(filter: {
        AND: {
            %s
            %s
            %s
        }
    })
    {
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
        % (source_filter, resource_filter, label_filter)
    ).replace("'", '"')


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


def get_credentials(credential_id):
    resp = run_graphql_query(credential_query, variables={"credentialId": credential_id})
    credentials = resp["data"]["credential"]
    if not credentials:
        raise OperationOutcome(f"Database using credentials ID {credential_id} does not exist")
    return credentials
