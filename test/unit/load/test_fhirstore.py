from unittest import mock

import fhirpipe.load.fhirstore as fhirstore


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
