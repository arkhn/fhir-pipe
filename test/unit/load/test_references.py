from unittest import mock

import fhirpipe.load.references as references
from test.unit import mock_config
from test.unit.load import mock_mongo_client


@mock.patch("fhirpipe.load.references.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_build_identifier_dict(*_):
    actual = references.build_identifier_dict()

    expected = {"Patient": {"0001": "123456"}, "HealthcareService": {"12345": "654321"}}

    assert actual == expected


@mock.patch("fhirpipe.load.references.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_bind_references(*_):
    reference_attributes = {
        "Patient": [("generalPractitioner",)],
    }
    identifier_dict = {
        "Patient": {"0001": "123456"},
        "HealthcareService": {"12345": "654321"},
    }

    references.bind_references(reference_attributes, identifier_dict)

    patients = mock_mongo_client[mock_config["fhirstore"]["database"]]["Patient"].find({})

    expected = {
        "_id": patients[0]["_id"],
        "id": "123456",
        "resourceType": "Patient",
        "gender": "female",
        "address": [{"city": "Paris", "country": "France"}],
        "identifier": [{"system": "system", "value": "0001"}],
        "generalPractitioner": [
            {
                "identifier": {"value": "12345"},
                "type": "HealthcareService",
                "reference": "HealthcareService/654321",
            }
        ],
    }

    assert patients[0] == expected

