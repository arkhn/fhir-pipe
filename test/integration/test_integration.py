from unittest import TestCase

import fhirpipe
import fhirpipe.run as run
from fhirpipe.load.fhirstore import get_mongo_client
from fhirpipe.extract.sql import get_connection


fhirpipe.set_global_config("test/integration/config-test.yml")


### Run from mapping file ###
def test_run_from_file():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=True,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=False,
        )
    assert_result_as_expected()


"""
### Run with graphQL queries ###
def test_run_from_gql():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping=None,
            source="mimic",
            resources=None,
            labels=None,
            reset_store=True,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=False,
        )
    assert_result_as_expected()
"""


### Run for a list of resources ###
def test_run_resource():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=["Patient", "not_existing_resource"],
            labels=["pat_label"],
            reset_store=True,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=False,
        )

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    assert mongo_client.list_collection_names() == ["Patient"]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    sample_simple = mongo_client["Patient"].find_one(
        {"identifier.0.value": id_sample_patient_simple}
    )
    sample_list = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient_list})

    assert_sample_comparison(sample_simple, sample_list, mongo_client, referencing_done=False)


### Run by batch ###
# When using batch processing, df can be cut at any place and some rows that should
# be squashed can be in different chunks
"""
def test_run_batch():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=True,
            chunksize=10,
            bypass_validation=True,
            multiprocessing=False,
        )
    assert_result_as_expected()
"""


def test_run_multiprocessing():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=True,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=True,
        )
    assert_result_as_expected()


### Run without resetting the mongo DB ###
def test_run_no_reset():
    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=True,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=False,
        )
    assert_result_as_expected()

    with get_connection() as c:
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=False,
            chunksize=None,
            bypass_validation=True,
            multiprocessing=False,
        )
    assert_result_as_expected(patients_count=200, services_count=326)


### Helper functions and variables for assertions ###
id_sample_patient_simple = "40655"
id_sample_patient_list = "10088"
expected_patients_count = 100
expected_services_count = 163


def assert_result_as_expected(
    patients_count=expected_patients_count, services_count=expected_services_count
):
    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    TestCase().assertCountEqual(
        mongo_client.list_collection_names(), ["Patient", "HealthcareService"]
    )
    assert_document_counts(mongo_client, patients_count, services_count)

    sample_simple = mongo_client["Patient"].find_one(
        {"identifier.0.value": id_sample_patient_simple}
    )
    sample_list = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient_list})

    assert_sample_comparison(sample_simple, sample_list, mongo_client)


def assert_document_counts(
    mongo_client, patients_count=expected_patients_count, services_count=expected_services_count,
):
    assert mongo_client["Patient"].count_documents({}) == patients_count
    assert mongo_client["HealthcareService"].count_documents({}) == services_count


def assert_sample_comparison(sample_simple, sample_list, mongo_client, referencing_done=False):
    vals_list = ["15067", "15068", "15069", "15070"]
    if referencing_done:
        ref_simple = mongo_client["HealthcareService"].find_one(
            {"identifier": {"$elemMatch": {"value": "48902"}}}, ["id"]
        )
        refs_list = [
            mongo_client["HealthcareService"].find_one(
                {"identifier": {"$elemMatch": {"value": val}}}, ["id"]
            )
            for val in vals_list
        ]

    expected_simple = {
        "_id": sample_simple["_id"],
        "id": sample_simple["id"],
        "resourceType": "Patient",
        "language": {"coding": [{"code": "ENGL"}]},
        "identifier": sample_simple["identifier"],
        "gender": "female",
        "birthDate": "1844-07-18",
        "address": {"city": "Paris", "country": "France"},
        "generalPractitioner": [{"identifier": {"value": "48902"}, "type": "HealthcareService"}],
    }
    if referencing_done:
        expected_simple["generalPractitioner"][0]["reference"] = ref_simple["id"]
    assert sample_simple == expected_simple

    assert sample_list == {
        "_id": sample_list["_id"],
        "id": sample_list["id"],
        "resourceType": "Patient",
        "identifier": sample_list["identifier"],
        "gender": "male",
        "birthDate": "2029-07-09",
        "address": {"city": "Paris", "country": "France"},
        "generalPractitioner": sample_list["generalPractitioner"],
    }
    if referencing_done:
        TestCase().assertCountEqual(
            sample_list["generalPractitioner"],
            [
                {"identifier": {"value": val}, "type": "HealthcareService", "reference": ref}
                for val, ref in zip(vals_list, refs_list)
            ],
        )
    else:
        TestCase().assertCountEqual(
            sample_list["generalPractitioner"],
            [
                {"identifier": {"value": val}, "type": "HealthcareService"}
                for val in vals_list
            ],
        )
