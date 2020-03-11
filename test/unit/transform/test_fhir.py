from unittest import mock
import pandas as pd
from pytest import raises

from fhirstore import ARKHN_CODE_SYSTEMS

import fhirpipe.transform.fhir as transform
from fhirpipe.analyze.attribute import Attribute
from fhirpipe.analyze.sql_column import SqlColumn


class mockdatetime:
    def strftime(self, _):
        return "now"


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_create_instance(mock_datetime, patient_mapping, fhir_concept_map_identifier):
    mock_datetime.now.return_value = mockdatetime()

    resource_mapping = patient_mapping

    attr_identifier = Attribute("identifier[0].value", columns=SqlColumn("a", "b"))
    attr_birthDate = Attribute("birthDate", columns=SqlColumn("a", "c"))
    attr_maritalStatus = Attribute("maritalStatus.coding[0].code", columns=SqlColumn("a", "d"))
    attr_generalPractitioner = Attribute(
        "generalPractitioner[0].type", static_inputs=["Practitioner"]
    )

    attributes = [attr_identifier, attr_birthDate, attr_maritalStatus, attr_generalPractitioner]

    row = {
        attr_maritalStatus: "D",
        attr_birthDate: "2000-10-10",
        attr_identifier: "A",
    }

    actual = transform.create_instance(row, resource_mapping, attributes)

    assert actual == {
        "meta": {
            "lastUpdated": "now",
            "tag": [
                {"system": ARKHN_CODE_SYSTEMS.source, "code": patient_mapping["source"]["id"]},
                {"system": ARKHN_CODE_SYSTEMS.resource, "code": patient_mapping["id"]},
            ],
        },
        "id": actual["id"],
        "identifier": [{"value": "A"}],
        "resourceType": "Patient",
        "birthDate": "2000-10-10",
        "maritalStatus": {"coding": [{"code": "D"}]},
        "generalPractitioner": [{"type": "Practitioner"}],
    }


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_create_resource(mock_datetime, patient_mapping, fhir_concept_map_identifier):
    mock_datetime.now.return_value = mockdatetime()

    resource_mapping = patient_mapping

    attr_identifier = Attribute("identifier[0].value", columns=SqlColumn("a", "b"))
    attr_birthDate = Attribute("birthDate", columns=SqlColumn("a", "c"))
    attr_maritalStatus = Attribute("maritalStatus.coding[0].code", columns=SqlColumn("a", "d"))
    attr_generalPractitioner = Attribute(
        "generalPractitioner[0].type", static_inputs=["Practitioner"]
    )

    attributes = [attr_identifier, attr_birthDate, attr_maritalStatus, attr_generalPractitioner]

    rows = pd.DataFrame(
        [
            {attr_maritalStatus: "D", attr_birthDate: "2000-10-10", attr_identifier: "A"},
            {attr_maritalStatus: "P", attr_birthDate: "2001-11-11", attr_identifier: "B"},
        ]
    )
    resource_mapping = patient_mapping

    actual = transform.create_resource(rows, resource_mapping, attributes)

    assert actual == [
        {
            "meta": {
                "lastUpdated": "now",
                "tag": [
                    {"system": ARKHN_CODE_SYSTEMS.source, "code": patient_mapping["source"]["id"]},
                    {"system": ARKHN_CODE_SYSTEMS.resource, "code": patient_mapping["id"]},
                ],
            },
            "id": actual[0]["id"],
            "identifier": [{"value": "A"}],
            "resourceType": "Patient",
            "birthDate": "2000-10-10",
            "maritalStatus": {"coding": [{"code": "D"}]},
            "generalPractitioner": [{"type": "Practitioner"}],
        },
        {
            "meta": {
                "lastUpdated": "now",
                "tag": [
                    {"system": ARKHN_CODE_SYSTEMS.source, "code": patient_mapping["source"]["id"]},
                    {"system": ARKHN_CODE_SYSTEMS.resource, "code": patient_mapping["id"]},
                ],
            },
            "id": actual[1]["id"],
            "identifier": [{"value": "B"}],
            "resourceType": "Patient",
            "birthDate": "2001-11-11",
            "maritalStatus": {"coding": [{"code": "P"}]},
            "generalPractitioner": [{"type": "Practitioner"}],
        },
    ]


@mock.patch("fhirpipe.transform.fhir.datetime", autospec=True)
def test_build_metadata(mock_datetime, patient_mapping):
    mock_datetime.now.return_value = mockdatetime()
    mapping = {
        "id": "resourceId",
        "definition": {"kind": "resource", "derivation": "specialization", "url": "u/r/l"},
        "source": {"id": "sourceId"},
    }
    metadata = transform.build_metadata(mapping)
    assert metadata == {
        "lastUpdated": "now",
        "tag": [
            {"system": ARKHN_CODE_SYSTEMS.source, "code": "sourceId"},
            {"system": ARKHN_CODE_SYSTEMS.resource, "code": "resourceId"},
        ],
    }

    mapping = {
        "id": "resourceId",
        "definition": {"kind": "resource", "derivation": "constraint", "url": "u/r/l"},
        "source": {"id": "sourceId"},
    }
    metadata = transform.build_metadata(mapping)
    assert metadata == {
        "lastUpdated": "now",
        "profile": ["u/r/l"],
        "tag": [
            {"system": ARKHN_CODE_SYSTEMS.source, "code": "sourceId"},
            {"system": ARKHN_CODE_SYSTEMS.resource, "code": "resourceId"},
        ],
    }


def test_fetch_values_from_dataframe():
    attr_identifier = Attribute("identifier[0].value", columns=SqlColumn("a", "b"))
    attr_birthDate = Attribute("birthDate", columns=SqlColumn("a", "c"))
    attr_maritalStatus = Attribute("maritalStatus.coding[0].code", columns=SqlColumn("a", "d"))

    attribute = attr_birthDate

    row = {
        attr_maritalStatus: "D",
        attr_birthDate: "2000-10-10",
        attr_identifier: "A",
    }

    value = transform.fetch_values_from_dataframe(row, attribute)

    assert value == "2000-10-10"


def test_handle_array_attributes():
    attr1 = Attribute("attr1", columns=SqlColumn("a", "b"))
    attr2 = Attribute("attr2", columns=SqlColumn("a", "c"))
    row = {
        attr1: ("A1", "A2", "A3"),
        attr2: "B",
    }
    attributes_in_array = {
        "path1": attr1,
        "path2": attr2,
    }

    value = transform.handle_array_attributes(attributes_in_array, row)

    assert value == [
        {"path1": "A1", "path2": "B"},
        {"path1": "A2", "path2": "B"},
        {"path1": "A3", "path2": "B"},
    ]

    # With mismatch in lengths
    row = {
        attr1: ("A1", "A2", "A3"),
        attr2: ("B1", "B2"),
    }
    with raises(AssertionError, match="mismatch in array lengths"):
        transform.handle_array_attributes(attributes_in_array, row)


def test_clean_fhir_object():
    dirty = {
        "a": {"b": [{"c": 123}, {"c": 123}, {"c": 123}, {"c": 222}, {"c": 222}]},
        "d": [{"e": {"f": 456}}, {"e": {"f": 456}}, {"e": 456}],
    }
    clean = transform.clean_fhir_object(dirty)

    expected = {
        "a": {"b": [{"c": 123}, {"c": 222}]},
        "d": [{"e": {"f": 456}}, {"e": 456}],
    }

    assert clean == expected


def test_get_position_first_index():
    path = ["root", "identifier[0]", "value"]
    index = transform.get_position_first_index(path)
    assert index == 1

    path = ["identifier", "value"]
    index = transform.get_position_first_index(path)
    assert index is None


def test_remove_index():
    path = "root.identifier[0]"
    result = transform.remove_index(path)
    assert result == "root.identifier"


def test_get_remove_root_path():
    init_path = "identifier.0.value"
    path = transform.remove_root_path(init_path, 2)
    assert path == "value"
