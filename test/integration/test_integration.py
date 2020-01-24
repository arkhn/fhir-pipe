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
    source=None,
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
    source="mimic",
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
    source=None,
)


@mock.patch("fhirpipe.cli.run.parse_args", return_value=args)
def test_run_resource(_):
    run.run()

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    assert mongo_client.list_collection_names() == ["Patient"]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    sample = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient})

    assert_sample_comparison(sample, mongo_client, referencing_done=False)


### Run by batch ###
args = argparse.Namespace(
    chunksize=10,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=True,
    resources=None,
    source=None,
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
    source=None,
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
    source=None,
)

args2 = argparse.Namespace(
    chunksize=None,
    config="test/integration/config-test.yml",
    mapping="test/fixtures/mimic_mapping.json",
    multiprocessing=False,
    reset_store=False,
    resources=None,
    source=None,
)


@mock.patch("fhirpipe.cli.run.parse_args", side_effect=[args1, args2])
# @mock.patch("fhirpipe.transform.fhir.bind_reference")
def test_run_no_reset(*_):
    run.run()
    assert_result_as_expected()

    run.run()
    assert_result_as_expected(patients_count=200, services_count=326)


### Helper functions and variables for assertions ###
id_sample_patient = "40655"
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

    sample = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient})

    assert_sample_comparison(sample, mongo_client)


def assert_document_counts(
    mongo_client,
    patients_count=expected_patients_count,
    services_count=expected_services_count,
):
    assert mongo_client["Patient"].count_documents({}) == patients_count
    assert mongo_client["HealthcareService"].count_documents({}) == services_count


def assert_sample_comparison(sample, mongo_client, referencing_done=True):
    assert sample["resourceType"] == "Patient"
    assert sample["language"] == "Engl"
    assert sample["gender"] == "female"
    assert sample["birthDate"] == "1844-07-18"
    assert sample["address"] == [
        {"city": "Paris", "country": "France"},
        {"city": "NY", "state": "NY state", "country": "USA"},
    ]

    if referencing_done:
        ref = mongo_client["HealthcareService"].find_one(
            {"identifier": {"$elemMatch": {"value": "48902"}}}, ["id"]
        )
        assert sample["generalPractitioner"] == [
            {"identifier": {"system": "HealthcareService", "value": ref["id"]}}
        ]
    else:
        assert sample["generalPractitioner"] == [
            {"identifier": {"system": "HealthcareService", "value": "48902"}}
        ]
