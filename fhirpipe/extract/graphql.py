import requests

import fhirpipe


def build_resources_query(selected_sources=None, selected_resources=None, selected_labels=None):
    # NOTE the curly braces have to be doubled in f-strings
    # NOTE The .replace("'", '"') is needed because the graphql needs to have
    # strings delimited by double quotes
    return f"""fragment entireColumn on Column {{
    id
    owner
    table
    column
    joins {{
        id
        tables {{
            id
            owner
            table
            column
        }}
    }}
}}

fragment entireInput on Input {{
    id
    sqlValue {{
        ...entireColumn
    }}
    script
    staticValue
}}

fragment a on Attribute {{
    id
    name
    fhirType
    mergingScript
    inputs {{
        ...entireInput
    }}
}}

query {{
    resources(filter: {{
        AND: {{
            { f'''source: {{
                name: {{ in: {selected_sources} }}
            }}''' if selected_sources else ""}
            { f"fhirType: {{ in: {selected_resources} }}" if selected_resources else ""}
            { f"label: {{ in: {selected_labels} }}" if selected_labels else ""}
        }}
    }})
    {{
        id
        fhirType
        primaryKeyOwner
        primaryKeyTable
        primaryKeyColumn
        attributes {{
            ...a
            children {{
                ...a
                children {{
                    ...a
                    children {{
                        ...a
                        children {{
                            ...a
                            children {{
                                ...a
                                children {{
                                    ...a
                                    children {{
                                        ...a
                                        children {{
                                            ...a
                                            children {{
                                                ...a
                                                children {{
                                                    ...a
                                                    children {{
                                                        ...a
                                                        children {{
                                                            ...a
                                                            children {{
                                                                ...a
                                                                children {{
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
""".replace(
        "'", '"'
    )


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
