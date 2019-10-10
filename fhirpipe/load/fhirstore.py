import fhirstore
from pymongo import MongoClient


def get_fhirstore():
    db_client = MongoClient(
        host=fhirpipe.global_config.fhirstore.host,
        port=fhirpipe.global_config.fhirstore.port,
        username=fhirpipe.global_config.fhirstore.user,
        password=fhirpipe.global_config.fhirstore.password,
    )
    return fhirstore.FHIRStore(
        db_client, fhirpipe.global_config.fhirstore.database
    )


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
