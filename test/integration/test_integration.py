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
            # resources=None,
            resources=["MedicationRequest"],
            labels=None,
            reset_store=True,
            chunksize=None,
            bypass_validation=False,
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
            bypass_validation=False,
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
            bypass_validation=False,
            multiprocessing=False,
        )

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    assert mongo_client.list_collection_names() == ["Patient"]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    assert_sample_patient_comparison(mongo_client)


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
            bypass_validation=False,
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
            bypass_validation=False,
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
            bypass_validation=False,
            multiprocessing=False,
        )
        run.run(
            connection=c,
            mapping="test/fixtures/mimic_mapping.json",
            source=None,
            resources=None,
            labels=None,
            reset_store=False,
            chunksize=None,
            bypass_validation=False,
            multiprocessing=False,
        )

    assert_result_as_expected(
        patients_count=2 * expected_patients_count,
        episode_of_care_count=2 * expected_episode_of_care_count,
        medication_request_count=2 * expected_med_req_count,
        diagnostic_report_count=2 * expected_diagnostic_report_count,
        practitioner_count=2 * expected_practitioner_count,
    )


### Helper functions and variables for assertions ###
expected_patients_count = 100
expected_episode_of_care_count = 265
expected_med_req_count = 10398
expected_diagnostic_report_count = 1761
expected_practitioner_count = 7567
id_sample_patient = "30831"
id_sample_med_req = "32600"


def assert_result_as_expected(
    patients_count=expected_patients_count,
    episode_of_care_count=expected_episode_of_care_count,
    medication_request_count=expected_med_req_count,
    diagnostic_report_count=expected_diagnostic_report_count,
    practitioner_count=expected_practitioner_count,
):
    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    TestCase().assertCountEqual(
        mongo_client.list_collection_names(),
        ["Patient", "EpisodeOfCare", "MedicationRequest", "DiagnosticReport", "Practitioner"],
    )
    assert_document_counts(
        mongo_client,
        patients_count,
        episode_of_care_count,
        medication_request_count,
        diagnostic_report_count,
        practitioner_count,
    )

    assert_sample_patient_comparison(mongo_client)
    assert_sample_med_req_comparison(mongo_client)


def assert_document_counts(
    mongo_client,
    patients_count=expected_patients_count,
    episode_of_care_count=expected_episode_of_care_count,
    medication_request_count=expected_med_req_count,
    diagnostic_report_count=expected_diagnostic_report_count,
    practitioner_count=expected_practitioner_count,
):
    assert mongo_client["Patient"].count_documents({}) == patients_count
    assert mongo_client["EpisodeOfCare"].count_documents({}) == episode_of_care_count
    assert mongo_client["MedicationRequest"].count_documents({}) == medication_request_count
    assert mongo_client["DiagnosticReport"].count_documents({}) == diagnostic_report_count
    assert mongo_client["Practitioner"].count_documents({}) == practitioner_count


def assert_sample_patient_comparison(mongo_client):
    sample_patient = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient})

    assert sample_patient == {
        "_id": sample_patient["_id"],
        "id": sample_patient["id"],
        "resourceType": "Patient",
        "identifier": [{"value": "30831"}],
        "gender": "female",
        "maritalStatus": {"coding": [{"code": "U"}]},
        "birthDate": "2063-07-05",
        "deceasedBoolean": True,
        "deceasedDateTime": "2130-11-03",
        "generalPractitioner": [{"type": "/Practitioner/"}],
    }


def assert_sample_med_req_comparison(mongo_client):
    sample_med_req = mongo_client["MedicationRequest"].find_one(
        {"identifier.0.value": id_sample_med_req}
    )

    assert sample_med_req == {
        "_id": sample_med_req["_id"],
        "id": sample_med_req["id"],
        "resourceType": "MedicationRequest",
        "identifier": [{"value": "32600"}],
        "subject": {"identifier": {"value": "42458"}, "type": "/Patient/"},
        "medicationCodeableConcept": {
            "coding": [
                {
                    "display": "Pneumococcal Vac Polyvalent",
                    "code": "6494300",
                    "system": "http://hl7.org/fhir/sid/ndc",
                }
            ],
            "text": "Pneumococcal Vac Polyvalent",
        },
        "status": "unknown",
        "intent": "order",
        "dosageInstruction": [{"route": {"coding": [{"code": "IM"}]}}],
        "dispenseRequest": {
            "validityPeriod": {"start": "2146-07-21", "end": "2146-07-22"},
            "quantity": {
                "value": 0.5,
                "unit": "mL",
                "code": "mL",
                "system": "https://unitsofmeasure.org/",
            },
        },
    }
