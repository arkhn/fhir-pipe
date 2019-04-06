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


def get_fhir_resource(database, resource, from_file=None):
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
        database_json = resources["data"]["database"]

        assert (
            database_json["name"] == database
        ), f"Database {database} is not in the graphql json resource"

        for resource_json in database_json["resources"]:
            if resource_json["name"] == resource:
                return resource_json

        raise FileNotFoundError(
            f"Resource {resource} not found in the graphql json resource"
        )

    else:
        response = run_query(get_query(database, resource))
        response = response["data"]["getResource"]

        return response
