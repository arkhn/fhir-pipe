from unittest import TestCase, mock
import pandas as pd

from fhirstore import ARKHN_CODE_SYSTEMS

import fhirpipe
import fhirpipe.run as run
from fhirpipe.load.fhirstore import get_mongo_client
from fhirpipe.extract.sql import build_db_url
from sqlalchemy import create_engine


fhirpipe.set_global_config("test/integration/config-test.yml")

lastUpdated = "2017-01-01T00:00:00Z"


class mockdatetime:
    def strftime(self, _):
        return lastUpdated


# Run from mapping file
@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_from_file(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=None,
        labels=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=False,
    )
    assert_result_as_expected()


"""
# Run with graphQL queries #
def test_run_from_gql():
    run.run(
        mapping=None,
        source="mimic",
        resources=None,
        labels=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=False,
    )
    assert_result_as_expected()
"""


# Run for a list of resources #
@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_resource(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=["Patient", "not_existing_resource"],
        labels=["pat_label"],
        override=False,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=False,
    )

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    db_collections = mongo_client.list_collection_names()
    assert len(db_collections) == 2
    assert "Patient" in db_collections
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    assert_sample_patient_comparison(mongo_client)


# Run by batch #
# When using batch processing, df can be cut at any place and some rows that should
# be squashed can be in different chunks
"""
def test_run_batch():
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=None,
        labels=None,
        override=False,
        chunksize=10,
        bypass_validation=False,
        multiprocessing=False,
    )
    assert_result_as_expected()
"""


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_multiprocessing(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=None,
        labels=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=True,
    )
    assert_result_as_expected()


# Run with the override option enabled, this will delete
# documents previously inserted using the same mapping rules
@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_override(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=["Patient"],
        labels=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=False,
    )
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resources=["Patient"],
        labels=None,
        override=True,
        chunksize=None,
        bypass_validation=False,
        multiprocessing=False,
    )
    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count


# Helper functions and variables for assertions #
engine = create_engine(build_db_url(fhirpipe.global_config["source"]))

expected_patients_count = pd.read_sql_query("SELECT COUNT(*) FROM patients", con=engine).at[
    0, "count"
]
expected_episode_of_care_count = (
    pd.read_sql_query(
        # include a filter in the count to reflect the filter contained in the mimic_mapping
        "SELECT COUNT(*) FROM admissions WHERE admissions.admittime >= '2150-08-29 18:20:00'",
        con=engine
    ).at[0, "count"]
    + pd.read_sql_query("SELECT COUNT(*) FROM icustays", con=engine).at[0, "count"]
)
expected_med_req_count = pd.read_sql_query("SELECT COUNT(*) FROM prescriptions", con=engine).at[
    0, "count"
]
expected_diagnostic_report_count = pd.read_sql_query(
    "SELECT COUNT(*) FROM diagnoses_icd", con=engine
).at[0, "count"]
expected_practitioner_count = pd.read_sql_query("SELECT COUNT(*) FROM caregivers", con=engine).at[
    0, "count"
]
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
        [
            "ConceptMap",
            "Patient",
            "EpisodeOfCare",
            "MedicationRequest",
            "DiagnosticReport",
            "Practitioner",
        ],
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
        "meta": {
            "lastUpdated": lastUpdated,
            "tag": [
                {"system": ARKHN_CODE_SYSTEMS.source, "code": "mimicSourceId"},
                {"system": ARKHN_CODE_SYSTEMS.resource, "code": "Patient_resourceId"},
            ],
        },
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
        "meta": {
            "lastUpdated": lastUpdated,
            "tag": [
                {"system": ARKHN_CODE_SYSTEMS.source, "code": "mimicSourceId"},
                {"system": ARKHN_CODE_SYSTEMS.resource, "code": "MedicationRequest_resourceId"},
            ],
        },
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
