from unittest import mock, TestCase
import argparse

import fhirpipe
import fhirpipe.cli.run as run
from fhirpipe.load.fhirstore import get_fhirstore, get_mongo_client


### Run from mapping file ###
args = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=True,
    resources=None,
    labels=None,
    sources=None,
    bypass_validation=False,
)


@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_from_file(_):
    run.run()
    assert_result_as_expected()


"""
### Run with graphQL queries ###
args = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping=None,
    multiprocessing=False,
    reset_store=True,
    resources=None,
    sources="mimic",
)

@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_from_gql(_):
    run.run()
    assert_result_as_expected()
"""

### Run for a list of resources ###
args = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=True,
    resources=["Patient", "not_existing_resource"],
    labels=["pat_label"],
    sources=None,
    bypass_validation=False,
)


@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_resource(_):
    run.run()

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    assert mongo_client.list_collection_names() == ["Patient"]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    sample_simple = mongo_client["Patient"].find_one(
        {"identifier.0.value": id_sample_patient_simple}
    )
    sample_list = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient_list})

    assert_sample_comparison(sample_simple, sample_list, mongo_client, referencing_done=False)


### Run by batch ###
args = argparse.Namespace(
    chunksize=10,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=True,
    resources=None,
    labels=None,
    sources=None,
    bypass_validation=False,
)


# When using batch processing, df can be cut at any place and some rows that should
# be squashed can be in different chunks
"""
@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_batch(_):
    run.run()
    assert_result_as_expected()
"""

### Run with multiprocessing ###
args = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=True,
    reset_store=True,
    resources=None,
    labels=None,
    sources=None,
    bypass_validation=False,
)


@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_multiprocessing(_):
    run.run()
    assert_result_as_expected()


### Run without resetting the mongo DB ###
args1 = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=True,
    resources=None,
    labels=None,
    sources=None,
    bypass_validation=False,
)

args2 = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=False,
    resources=None,
    labels=None,
    sources=None,
    bypass_validation=False,
)


@mock.patch("fhirpipe.cli.run.parse_args", side_effect=[args1, args2])
# @mock.patch("fhirpipe.transform.fhir.bind_reference")
def test_run_no_reset(*_):
    run.run()
    assert_result_as_expected()

    run.run()
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


def assert_sample_comparison(sample_simple, sample_list, mongo_client, referencing_done=True):

    if referencing_done:
        ref_simple = mongo_client["HealthcareService"].find_one(
            {"identifier": {"$elemMatch": {"value": "48902"}}}, ["id"]
        )
        refs_list = [
            mongo_client["HealthcareService"].find_one(
                {"identifier": {"$elemMatch": {"value": val}}}, ["id"]
            )
            for val in ["15067", "15068", "15069", "15070"]
        ]

    assert sample_simple == {
        "_id": sample_simple["_id"],
        "id": sample_simple["id"],
        "resourceType": "Patient",
        "language": "Engl",
        "identifier": sample_simple["identifier"],
        "gender": "female",
        "birthDate": "1844-07-18",
        "address": [
            {"city": "Paris", "country": "France"},
            {"city": "NY", "state": "NY state", "country": "USA"},
        ],
        "generalPractitioner": [
            {
                "identifier": {
                    "system": "HealthcareService",
                    "value": ref_simple["id"] if referencing_done else "48902",
                }
            }
        ],
    }

    assert sample_list == {
        "_id": sample_list["_id"],
        "id": sample_list["id"],
        "resourceType": "Patient",
        "identifier": sample_list["identifier"],
        "gender": "male",
        "birthDate": "2029-07-09",
        "address": [
            {"city": "Paris", "country": "France"},
            {"city": "NY", "state": "NY state", "country": "USA"},
        ],
        "generalPractitioner": [
            {"identifier": {"system": "HealthcareService", "value": ref["id"]}} for ref in refs_list
        ]
        if referencing_done
        else [
            {"identifier": {"system": "HealthcareService", "value": val}}
            for val in ["15067", "15068", "15069", "15070"]
        ],
    }
