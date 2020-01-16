from unittest import mock

import fhirpipe.load.fhirstore as fhirstore
from test.unit import mock_config
from test.unit.load import mock_mongo_client


@mock.patch("fhirpipe.load.fhirstore.get_fhirstore", return_value=mock.Mock())
def test_save_many(_):
    fhirstore.save_many(
        [
            {"name": "instance1", "value": 1},
            {"name": "instance2", "value": 2},
            {"name": "instance3", "value": 3},
        ]
    )

    store = fhirstore.get_fhirstore()

    assert store.create.call_count == 3
    store.create.assert_has_calls(
        [
            mock.call({"name": "instance1", "value": 1}),
            mock.call({"name": "instance2", "value": 2}),
            mock.call({"name": "instance3", "value": 3}),
        ]
    )


@mock.patch("fhirpipe.load.fhirstore.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_find_fhir_resource(*_):

    assert fhirstore.find_fhir_resource("Patient", "0001") == "123456"

    # Use URI that doesn't exist:
    assert fhirstore.find_fhir_resource("Observation", "0001") is None

    # With identifier value that doesn't exist
    assert fhirstore.find_fhir_resource("Observation", "0000") is None
