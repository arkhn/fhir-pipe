from functools import partial

import fhirpipe
from fhirpipe.load.fhirstore import get_mongo_client


def build_identifier_dict():
    db_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]
    resources = db_client.list_collection_names()

    identifier_dict = {}

    for resource in resources:

        results = db_client[resource].find(
            {"identifier": {"$elemMatch": {"value": {"$exists": True}}}},
            ["id", "identifier"],
        )

        identifier_dict[resource] = {}
        for r in results:
            for r_identifier in r["identifier"]:
                identifier_dict[resource][r_identifier["value"]] = r["id"]

    return identifier_dict


def bind_references(reference_attributes, identifier_dict, pool=None):
    db_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    for resource, references in reference_attributes.items():
        collection = db_client[resource].find({})

        if pool:
            pool.map(
                partial(
                    bind_references_for_doc,
                    resource=resource,
                    references=references,
                    identifier_dict=identifier_dict,
                ),
                collection,
            )
        else:
            for document in collection:
                bind_references_for_doc(document, resource, references, identifier_dict)


def bind_references_for_doc(document, resource, references, identifier_dict):
    db_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    for path in references:
        # Extract the sub-tree which is a reference
        rec_bind_reference(document, identifier_dict, path)

    db_client[resource].replace_one({"_id": document["_id"]}, document)


def rec_bind_reference(fhir_object, identifier_dict, path):
    """
    Analyse a reference and replace the provided identifier
    with official FHIR uri if the resource reference exists.

    args:
        fhir_object: the fhir object to parse
        identifier_dict: a dictionary where the keys are
            identifier values and the values are fhir ids
        path: path to reference attribute

    return:
        a fhir_object where valid references are now FHIR uris
    """
    if isinstance(fhir_object, dict):
        if path:
            rec_bind_reference(fhir_object[path[0]], identifier_dict, path[1:])

        # We have the reference attribute to bind
        # First we check that the reference has been provided
        elif fhir_object and fhir_object["identifier"]["value"]:
            # get id
            identifier = fhir_object["identifier"]["value"]
            # get referenced type (URI)
            uri = fhir_object["identifier"]["system"]

            # Get the fhir id
            fhir_uri = (
                identifier_dict[uri][identifier]
                if uri in identifier_dict and identifier in identifier_dict[uri]
                else None
            )

            # If an instance was found, replace the provided
            # identifier with FHIR id found
            if fhir_uri is not None:
                fhir_object["identifier"]["value"] = fhir_uri

    elif isinstance(fhir_object, list):
        for child in fhir_object:
            rec_bind_reference(child, identifier_dict, path)
