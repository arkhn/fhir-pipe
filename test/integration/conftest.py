from pytest import fixture

from fhirpipe.load.fhirstore import get_fhirstore


cm_mimic_gender = {
    "description": "Map mimic gender to fhir gender",
    "group": [
        {
            "element": [
                {"code": "M", "target": [{"code": "male", "equivalence": "equivalent"}]},
                {"code": "F", "target": [{"code": "female", "equivalence": "equivalent"}]},
            ],
            "source": "MimicGender",
            "target": "AdministrativeGender",
        }
    ],
    "id": "04a8ab8d-9a58-48d3-851f-9c00afbbf1d1",
    "name": "MimicGender > AdministrativeGender",
    "resourceType": "ConceptMap",
    "sourceUri": "",
    "targetUri": "",
    "title": "MimicGender > AdministrativeGender",
}


@fixture
def with_concept_maps():
    store = get_fhirstore()
    store.bootstrap(resource="ConceptMap")
    store.create(cm_mimic_gender)


@fixture(autouse=True)
def reset_store():
    store = get_fhirstore()
    store.reset()
