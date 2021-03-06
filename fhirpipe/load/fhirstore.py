import logging

from pymongo import MongoClient
from tqdm import tqdm
from jsonschema import ValidationError
import fhirstore

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
            get_mongo_client(), None, fhirpipe.global_config["fhirstore"]["database"]
        )
        _fhirstore.resume()
    return _fhirstore


def save_many(instances, bypass_validation=False, multi_processing=False):
    """
    Save instances of FHIR resources in MongoDB through fhirstore.

    args:
        instances (list): list of instances
    """
    store = get_fhirstore()
    if multi_processing:
        store.resume()

    instances = tqdm(instances)
    for instance in instances:
        try:
            store.create(instance, bypass_document_validation=bypass_validation)
        except ValidationError as e:
            logging.error(
                f"Validation failed for resource {instance} at "
                f"{'.'.join(e.schema_path)}: {e.message}"
            )
        instances.refresh()


def get_resource_instances(resource_id, resource_type):
    global _client
    store = _client[fhirpipe.global_config["fhirstore"]["database"]]
    return store[resource_type].find(
        {
            "meta.tag": {
                "$elemMatch": {
                    "code": {"$eq": resource_id},
                    "system": {"$eq": fhirstore.ARKHN_CODE_SYSTEMS.resource},
                }
            }
        }
    )
