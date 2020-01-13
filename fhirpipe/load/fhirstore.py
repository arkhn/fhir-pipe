import fhirstore
from pymongo import MongoClient
from tqdm import tqdm

import fhirpipe


_client = None


def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(
            host=fhirpipe.global_config["fhirstore"]["host"],
            port=fhirpipe.global_config["fhirstore"]["port"],
            username=fhirpipe.global_config["fhirstore"]["user"],
            password=fhirpipe.global_config["fhirstore"]["password"],
        )
    return _client


_fhirstore = None


def get_fhirstore():
    global _fhirstore
    if _fhirstore is None:
        _fhirstore = fhirstore.FHIRStore(
            get_mongo_client(), fhirpipe.global_config["fhirstore"]["database"]
        )
    return _fhirstore


def save_many(instances):
    """
    Save instances of FHIR resources in MongoDB through fhirstore.

    args:
        instances (list): list of instances
    """
    store = get_fhirstore()
    instances = tqdm(instances)
    for instance in instances:
        store.create(instance)
        instances.refresh()


fhir_ids = {}


def find_fhir_resource(uri, identifier):
    """
    Return the first FHIR instance of some resource_type where the
    identifier matches some identifier, if any is found.

    args:
        resource_type (str): name of the Fhir resource to search for
        identifier (str): the provided id which could be an identifier of
            some instance of the resource_type

    return:
        the fhir id of the instance is there is one found of resource_type
        which has an identifier matching the provided identifier,
        else None
    """
    db_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    # NOTE For now, URI simply consists in the resource name, need discussion about this
    resource_type = uri

    if resource_type not in fhir_ids:
        # If URI not found, don't do anything
        if resource_type not in db_client.list_collection_names():
            return

        results = db_client[resource_type].find(
            {"identifier": {"$elemMatch": {"value": {"$exists": True}}}},
            ["id", "identifier"],
        )

        fhir_ids[resource_type] = {}
        for r in results:
            for r_identifier in r["identifier"]:
                fhir_ids[resource_type][r_identifier["value"]] = r["id"]

    return fhir_ids[resource_type].get(identifier)
