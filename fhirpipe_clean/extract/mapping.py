import os
import logging

from fhirpipe_clean.extract.graphql import *


def get_resources(source_name, from_file=None):
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
        source = run_graphql_query(source_info_query, variables={"sourceName": source_name})
        source_id = source["data"]["sourceInfo"]["id"]

        # Check that Resource exists for given Source
        available_resources = run_graphql_query(
            available_resources_query, variables={"sourceId": source_id}
        )
        return available_resources["data"]["availableResources"]

def prune_fhir_resource(resource_structure):
    """ Remove FHIR attributes that have not been mapped
    from resource structure object.
    """
    resource_structure["attributes"][:] = [attr for attr in resource_structure["attributes"] if rec_prune_resource(attr)]
    return resource_structure

def rec_prune_resource(attr_structure):
    """ Helper recursive function called by prune_fhir_resource.
    """
    if isinstance(attr_structure, dict):
        if attr_structure["attributes"]:
            attr_structure["attributes"][:] = [attr for attr in attr_structure["attributes"] if rec_prune_resource(attr)]
            return len(attr_structure["attributes"]) > 0
        elif attr_structure["inputColumns"]:
            return True
        else:
            del attr_structure
            return False
        
    elif isinstance(attr_structure, list):
        attr_structure[:] = [attr for attr in attr_structure if rec_prune_resource(attr)]
        return len(attr_structure) > 0
    
    else:
        raise Exception("attr_structure not a dict nor a list.")

def get_identifier_table(resource_structure, extended_get=False):
    """
    Analyse a resource mapping rules and return the mapping rule for
    the identifier

    args:
        resource_structure: the object containing all the mapping rules
        extended_get (bool): search for the identifier table not only in
            identifier attributes (default: False)

    Return:
        The table referenced by the identifier mapping rule
    """

    targets = []
    for attribute in resource_structure["attributes"]:
        if attribute["name"] == "identifier" or extended_get:
            search_for_input_columns(attribute, targets)

    if len(targets) < 1:
        if extended_get:
            raise AttributeError("There is no mapping rule for the identifier of this resource")
        else:
            return get_identifier_table(resource_structure, extended_get=True)
    else:
        if len(targets) > 1:
            logging.warning(
                "Warning: Too many choices for the right main table for building SQL request,\
taking the first one."
            )
        return targets[0]

def search_for_input_columns(obj, targets):
    """
    Inspect a mapping object of an identifier and list all tables used
    in mapping rules

    args:
        obj: mapping object of an identifier
        targets: a list to append the tables found

    returns:
        None as the results are appended to the targets list
    """
    if isinstance(obj, dict):
        if "inputColumns" in obj and len(obj["inputColumns"]) > 0:
            for input_col in obj["inputColumns"]:
                if input_col["table"]:
                    targets.append(input_col["table"])
        elif "attributes" in obj:
            search_for_input_columns(obj["attributes"], targets)
    elif isinstance(obj, list):
        for o in obj:
            search_for_input_columns(o, targets)