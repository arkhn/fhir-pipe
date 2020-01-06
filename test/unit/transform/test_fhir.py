import json
import pandas as pd
from unittest import mock

import fhirpipe.transform.fhir as transform

from test.unit.transform import PATIENT_LIGHT_RESOURCE


def test_create_fhir_object():
    row = {
        "ICSF.PATIENT.NOPAT": "100092",
        "ICSF.PATIENT.NOMPAT": "Chirac",
        "ICSF.PATIENT.PREPAT": "Jacques",
        "ICSF.PATIENT.PREPATSUITE": "François",
        "ICSF.PATIENT.SEXE": "M",
    }
    resource_structure = json.loads(PATIENT_LIGHT_RESOURCE)
    actual = transform.create_fhir_object(row, resource_structure)

    assert actual == {
        "id": actual["id"],
        "resourceType": "Patient",
        "identifier": [{"value": "100092"}],
        "name": [{"family": "Chirac", "given": ["Jacques", "François"]}],
        "gender": "M",
    }


def test_create_resource():
    rows = pd.DataFrame([
        {
            "ICSF.PATIENT.NOPAT": "100092",
            "ICSF.PATIENT.NOMPAT": "Chirac",
            "ICSF.PATIENT.PREPAT": "Jacques",
            "ICSF.PATIENT.PREPATSUITE": "François",
            "ICSF.PATIENT.SEXE": "M",
        },
        {
            "ICSF.PATIENT.NOPAT": "100093",
            "ICSF.PATIENT.NOMPAT": "Mitterrand",
            "ICSF.PATIENT.PREPAT": "François",
            "ICSF.PATIENT.PREPATSUITE": "Maurice",
            "ICSF.PATIENT.SEXE": "M",
        },
    ])
    resource_structure = json.loads(PATIENT_LIGHT_RESOURCE)
    actual = transform.create_resource(rows, resource_structure)

    assert actual == [
        {
            "id": actual[0]["id"],
            "resourceType": "Patient",
            "identifier": [{"value": "100092"}],
            "name": [{"family": "Chirac", "given": ["Jacques", "François"]}],
            "gender": "M",
        },
        {
            "id": actual[1]["id"],
            "resourceType": "Patient",
            "identifier": [{"value": "100093"}],
            "name": [{"family": "Mitterrand", "given": ["François", "Maurice"]}],
            "gender": "M",
        },
    ]


@mock.patch("fhirpipe.transform.fhir.find_fhir_resource", return_value="dummy_uri")
def test_bind_reference(find_resource):
    obj = {"identifier": {"value": "dummy_value"}, "other_key": {"other_value"}}

    transform.bind_reference(
        obj,
        {"type": "Reference(abc|def)", "name": "fhir name"},
    )

    assert obj == {"identifier": {"value": "dummy_uri"}, "other_key": {"other_value"}}
