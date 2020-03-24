from unittest import TestCase, mock
import pandas as pd

from fhirstore import ARKHN_CODE_SYSTEMS

import fhirpipe
import fhirpipe.run as run
from fhirpipe.load.fhirstore import get_mongo_client
from fhirpipe.extract.extractor import Extractor
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
        resource_ids=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=False,
    )
    assert_result_as_expected()


"""
# Run with graphQL queries #
def test_run_from_gql():
    run.run(
        mapping=None,
        resource_ids=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=False,
    )
    assert_result_as_expected()
"""


# Run by batch #
# When using batch processing, df can be cut at any place and some rows that should
# be squashed can be in different chunks
"""
def test_run_batch():
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        source=None,
        resource_ids=None,
        labels=None,
        override=False,
        chunksize=10,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=False,
    )
    assert_result_as_expected()
"""


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_multiprocessing(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/mimic_mapping.json",
        resource_ids=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=True,
    )
    assert_result_as_expected()


# Run with the override option enabled, this will delete
# documents previously inserted using the same mapping rules
@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_override(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/small_mimic_mapping.json",
        resource_ids=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=False,
    )
    run.run(
        mapping="test/fixtures/small_mimic_mapping.json",
        resource_ids=None,
        override=True,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=True,
        multiprocessing=False,
    )
    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count
    assert mongo_client["Practitioner"].count_documents({}) == expected_admissions_count


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_run_ref_binding(mock_datetime, with_concept_maps):
    mock_datetime.now.return_value = mockdatetime()
    run.run(
        mapping="test/fixtures/small_mimic_mapping.json",
        resource_ids=None,
        override=False,
        chunksize=None,
        bypass_validation=False,
        skip_ref_binding=False,
        multiprocessing=False,
    )

    mongo_client = get_mongo_client()[fhirpipe.global_config["fhirstore"]["database"]]

    db_collections = mongo_client.list_collection_names()
    assert "Patient" in db_collections
    assert "Practitioner" in db_collections
    assert mongo_client["Patient"].count_documents({}) == expected_patients_count

    compare_sample_patient_referencing(mongo_client)


# Helper functions and variables for assertions #
engine = create_engine(Extractor.build_db_url(fhirpipe.global_config["source"]))

expected_patients_count = pd.read_sql_query("SELECT COUNT(*) FROM patients", con=engine).at[
    0, "count"
]
expected_episode_of_care_count = (
    pd.read_sql_query(
        # include a filter in the count to reflect the filter contained in the mimic_mapping
        "SELECT COUNT(*) FROM admissions WHERE admissions.admittime >= '2150-08-29 18:20:00'",
        con=engine,
    ).at[0, "count"]
    + pd.read_sql_query("SELECT COUNT(*) FROM icustays", con=engine).at[0, "count"]
)
expected_med_req_count = pd.read_sql_query("SELECT COUNT(*) FROM prescriptions", con=engine).at[
    0, "count"
]
expected_diagnostic_report_count = pd.read_sql_query(
    "SELECT COUNT(*) FROM diagnoses_icd", con=engine
).at[0, "count"]
expected_admissions_count = pd.read_sql_query("SELECT COUNT(*) FROM admissions", con=engine).at[
    0, "count"
]
id_sample_patient = "30831"
id_sample_med_req = "32600"


def assert_result_as_expected(
    patients_count=expected_patients_count,
    episode_of_care_count=expected_episode_of_care_count,
    medication_request_count=expected_med_req_count,
    diagnostic_report_count=expected_diagnostic_report_count,
    admissions_count=expected_admissions_count,
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
        admissions_count,
    )

    compare_sample_patient(mongo_client)
    compare_sample_med_req(mongo_client)


def assert_document_counts(
    mongo_client,
    patients_count=expected_patients_count,
    episode_of_care_count=expected_episode_of_care_count,
    medication_request_count=expected_med_req_count,
    diagnostic_report_count=expected_diagnostic_report_count,
    admissions_count=expected_admissions_count,
):
    assert mongo_client["Patient"].count_documents({}) == patients_count
    assert mongo_client["EpisodeOfCare"].count_documents({}) == episode_of_care_count
    assert mongo_client["MedicationRequest"].count_documents({}) == medication_request_count
    assert mongo_client["DiagnosticReport"].count_documents({}) == diagnostic_report_count
    assert mongo_client["Practitioner"].count_documents({}) == admissions_count


def compare_sample_patient(mongo_client):
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
        "generalPractitioner": [
            {"identifier": {"value": "126179"}, "type": "Practitioner"},
            {"identifier": {"value": "146893"}, "type": "Practitioner"},
        ],
    }


def compare_sample_patient_referencing(mongo_client):
    sample_patient = mongo_client["Patient"].find_one({"identifier.0.value": id_sample_patient})

    id1 = mongo_client["Practitioner"].find_one({"identifier.0.value": "126179"})["id"]
    id2 = mongo_client["Practitioner"].find_one({"identifier.0.value": "146893"})["id"]

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
        "generalPractitioner": [
            {
                "reference": f"Practitioner/{id1}",
                "identifier": {"value": "126179"},
                "type": "Practitioner",
            },
            {
                "reference": f"Practitioner/{id2}",
                "identifier": {"value": "146893"},
                "type": "Practitioner",
            },
        ],
    }


def compare_sample_med_req(mongo_client):
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
