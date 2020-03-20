from pytest import fixture
from unittest import mock

from fhirpipe.references import reference_binder

from test.unit.conftest import mock_config
from test.unit.references import mock_mongo_client


id_example_pat_1 = "123456"
id_example_pat_2 = "654321"


@fixture
def binder():
    return reference_binder.ReferenceBinder(mock.Mock())


@fixture(autouse=True)
def init_mongo():
    database = mock_mongo_client.get_database("fhirstore")

    database["Patient"].delete_many({})
    database["HealthcareService"].delete_many({})

    database["Patient"].insert_many(
        [
            {
                "_id": "987654321",
                "id": id_example_pat_1,
                "resourceType": "Patient",
                "identifier": [
                    {"system": "system", "value": "0001"},
                    {
                        "system": "system",
                        "value": "1001",
                        "type": {"coding": [{"system": "SSN", "code": "ssn_val"}]},
                    },
                ],
                "generalPractitioner": [
                    {"identifier": {"value": "12345"}, "type": "HealthcareService"}
                ],
            },
            {
                "_id": "123456789",
                "id": id_example_pat_2,
                "resourceType": "Patient",
                "identifier": [
                    {"system": "system", "value": "0002"},
                    {"value": "1002", "type": {"coding": [{"system": "SSN", "code": "val_ssn"}]}},
                ],
                "generalPractitioner": [
                    {"type": "Practitioner", "identifier": {"system": "sys", "value": "9467"}}
                ],
            },
        ]
    )

    database["HealthcareService"].insert_one(
        {
            "_id": "123456789",
            "id": "654321",
            "resourceType": "HealthcareService",
            "identifier": [{"value": "12345"}],
        }
    )


@mock.patch("fhirpipe.references.reference_binder.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_bind_references_for_instance(get_mongo_mock, binder):
    # mock fhirstore update
    def update_mongo(resource_type, instance_id, resource):
        get_mongo_mock()["fhirstore"][resource_type].find_one_and_replace(
            {"id": instance_id}, resource
        )

    binder.fhirstore.update.side_effect = update_mongo

    # mock indentifiers_store
    binder.indentifiers_store = {"Practitioner": {("9467", "sys", None, None): "ref_id"}}

    instance = {
        "_id": "123456789",
        "identifier": [{"system": "system", "value": "0002"}],
        "generalPractitioner": [
            {"type": "Practitioner", "identifier": {"system": "sys", "value": "9467"}}
        ],
        "id": "654321",
        "resourceType": "Patient",
    }
    reference_paths = ["generalPractitioner[0]"]
    binder.bind_references_for_instance(instance, reference_paths)

    actual = get_mongo_mock()["fhirstore"]["Patient"].find({"id": "654321"})[0]

    expected = instance
    expected["generalPractitioner"][0]["reference"] = "Practitioner/ref_id"

    assert actual == expected


@mock.patch("fhirpipe.references.reference_binder.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_get_collection_map(_, binder):
    map1 = binder.get_collection_map("Patient")

    assert map1 == {
        ("0001", "system", None, None): id_example_pat_1,
        ("1001", "system", "SSN", "ssn_val"): id_example_pat_1,
        ("0002", "system", None, None): id_example_pat_2,
        ("1002", None, "SSN", "val_ssn"): id_example_pat_2,
    }
    assert binder.indentifiers_store == {"Patient": map1}


def test_add_reference(binder):
    resource_mapping = {
        "id": "resource_id",
        "definition": {"type": "Patient"},
        "attributes": [],
    }
    path = "path.to.reference"

    binder.add_reference(resource_mapping, path)

    assert binder.map_resource_type == {"resource_id": "Patient"}
    assert binder.map_resource_references == {"resource_id": ["path.to.reference"]}

    other_path = "other.path"
    binder.add_reference(resource_mapping, other_path)

    assert binder.map_resource_type == {"resource_id": "Patient"}
    assert binder.map_resource_references == {"resource_id": ["path.to.reference", "other.path"]}


def test_find_sub_fhir_object():
    fhir_object = {
        "identifier": [{"value": "identifier_val", "system": "identifier_sys"}],
        "meta": {"lastUpdated": "today", "tag": ["tag1", "tag2"]},
        "array": [{"attr": {"attr_ref": {"field": "ref_field"}}}],
    }
    path = "array[0].attr.attr_ref"

    sub_fhir_obj = reference_binder.ReferenceBinder.find_sub_fhir_object(fhir_object, path)

    assert sub_fhir_obj == {"field": "ref_field"}
