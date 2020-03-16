from pytest import fixture
from unittest import mock

from fhirpipe.references import reference_binder

from test.unit.conftest import mock_config
from test.unit.references import mock_mongo_client


@fixture
def binder():
    return reference_binder.ReferenceBinder(mock.Mock())


@mock.patch("fhirpipe.references.reference_binder.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_bind_references_for_instance(mongo_mock, binder):
    # mock fhirstore update
    def update_mongo(resource_type, instance_id, resource):
        mongo_mock()["fhirstore"][resource_type].find_one_and_replace({"id": instance_id}, resource)

    binder.fhirstore.update.side_effect = update_mongo


    # mock indentifiers_store
    binder.indentifiers_store = {"Practitioner": {("9467", "sys"): "ref_id"}}

    instance = {
        "_id": "5e6b5de381ee0cdbdfa17ceb",
        "identifier": [{"system": "system", "value": "0002"}],
        "generalPractitioner": [
            {"type": "Practitioner", "identifier": {"system": "sys", "value": "9467"}}
        ],
        "id": "f900bb69-408d-4cf1-af62-3da7def97bcc",
        "resourceType": "Patient",
    }
    reference_paths = ["generalPractitioner[0]"]
    binder.bind_references_for_instance(instance, reference_paths)

    actual = mongo_mock()["fhirstore"]["Patient"].find(
        {"id": "f900bb69-408d-4cf1-af62-3da7def97bcc"}
    )[0]

    expected = instance
    expected["generalPractitioner"][0]["reference"] = "Practitioner/ref_id"

    assert actual == expected

@mock.patch("fhirpipe.references.reference_binder.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_get_collection_map(_, binder):
    map1 = binder.get_collection_map("Patient")

    assert map1 == {("0001", "system"): "123456", ("0002", "system"): "654321"}
    assert binder.indentifiers_store == {
        "Patient": {("0001", "system"): "123456", ("0002", "system"): "654321"}
    }


def test_add_reference(binder):
    resource_mapping = {
        "id": "resource_id",
        "definitionId": "Patient",
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


@mock.patch("fhirpipe.load.references.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_build_identifier_dict(*_):
    # actual = references.build_identifier_dict()

    # expected = {"Patient": {"0001": "123456"}, "HealthcareService": {"12345": "654321"}}

    # assert actual == expected
    pass


@mock.patch("fhirpipe.load.references.get_mongo_client", return_value=mock_mongo_client)
@mock.patch("fhirpipe.load.fhirstore.fhirpipe.global_config", mock_config)
def test_bind_references(*_):
    # reference_attributes = {
    #     "Patient": [("generalPractitioner",)],
    # }
    # identifier_dict = {
    #     "Patient": {"0001": "123456"},
    #     "HealthcareService": {"12345": "654321"},
    # }

    # references.bind_references(reference_attributes, identifier_dict)

    # patients = mock_mongo_client[mock_config["fhirstore"]["database"]]["Patient"].find({})

    # expected = {
    #     "_id": patients[0]["_id"],
    #     "id": "123456",
    #     "resourceType": "Patient",
    #     "gender": "female",
    #     "address": [{"city": "Paris", "country": "France"}],
    #     "identifier": [{"system": "system", "value": "0001"}],
    #     "generalPractitioner": [
    #         {
    #             "identifier": {"value": "12345"},
    #             "type": "HealthcareService",
    #             "reference": "HealthcareService/654321",
    #         }
    #     ],
    # }

    # assert patients[0] == expected
    pass
