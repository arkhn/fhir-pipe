import json
import fhirpipe.transform.transform as transform

from test.unit.transform import PATIENT_LIGHT_RESOURCE


def test_create_fhir_object():
    row = {
        "ICSF.PATIENT.NOPAT": "100092",
        "ICSF.PATIENT.NOMPAT": "Chirac",
        "ICSF.PATIENT.PREPAT": "Jacques",
        "ICSF.PATIENT.PREPATSUITE": "François",
        "ICSF.PATIENT.SEXE": "M",
    }
    resource = "Patient"
    resource_patient_structure = json.loads(PATIENT_LIGHT_RESOURCE)
    fhir_object = transform.create_fhir_object(
        row, resource_patient_structure, resource
    )
    fhir_id = fhir_object["id"]
    print(fhir_object)
    assert fhir_object == {
        "id": fhir_id,
        "resourceType": "Patient",
        "identifier": [{"value": "100092"}],
        "name": [{"family": "Chirac", "given": ["Jacques", "François"]}],
        "gender": "M",
    }
