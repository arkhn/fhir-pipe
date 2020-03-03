from unittest import mock

from fhirpipe.analyze.concept_map import get_concept_maps, ConceptMap

from test.unit.conftest import mock_config


cm_123 = {
    "group": [
        {
            "element": [
                {"code": "1", "target": [{"code": "A"}]},
                {"code": "2", "target": [{"code": "B"}]},
                {"code": "3", "target": [{"code": "C"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm123",
}

cm_456 = {
    "group": [
        {
            "element": [
                {"code": "4", "target": [{"code": "D"}]},
                {"code": "5", "target": [{"code": "E"}]},
                {"code": "6", "target": [{"code": "F"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm456",
}

cm_789 = {
    "group": [
        {
            "element": [
                {"code": "7", "target": [{"code": "G"}]},
                {"code": "8", "target": [{"code": "H"}]},
                {"code": "9", "target": [{"code": "I"}]},
            ],
        }
    ],
    "resourceType": "ConceptMap",
    "title": "cm789",
}


def mock_api_get_maps(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "https://url/api/ConceptMap/123":
        return MockResponse(cm_123, 200,)
    elif args[0] == "https://url/api/ConceptMap/456":
        return MockResponse(cm_456, 200,)
    elif args[0] == "https://url/api/ConceptMap/789":
        return MockResponse(cm_789, 200,)
    return MockResponse(None, 404)


def test_concept_map_init():
    fhir_concept_map = {
        "title": "test_concept_map",
        "sourceUri": "sourceUri",
        "targetUri": "targetUri",
        "group": [
            {
                "source": "src",
                "target": "trgt",
                "element": [
                    {"code": "src_code", "target": [{"code": "trgt_code"}, {"code": "not_used"}]},
                    {"code": "code1", "target": [{"code": "code2"}]},
                ],
            },
            {
                "source": "sys1",
                "target": "sys2",
                "element": [
                    {"code": "11", "target": [{"code": "12"}]},
                    {"code": "21", "target": [{"code": "22"}]},
                    {"code": "31", "target": [{"code": "32"}]},
                ],
            },
        ],
    }

    concept_map = ConceptMap(fhir_concept_map)

    assert concept_map.columns == []
    assert concept_map.title == "test_concept_map"
    assert concept_map.mapping == {
        "src_code": "trgt_code",
        "code1": "code2",
        "11": "12",
        "21": "22",
        "31": "32",
    }


@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_get_concept_maps():
    resource_mapping = {
        "attributes": [
            {"inputs": [{"conceptMapId": "123"}, {"conceptMapId": "456"}]},
            {"inputs": [{"conceptMapId": "789"}]},
        ]
    }
    concept_maps = get_concept_maps(resource_mapping)

    assert concept_maps == {
        "123": ConceptMap(cm_123),
        "456": ConceptMap(cm_456),
        "789": ConceptMap(cm_789),
    }


@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_fetch_concept_map():
    concept_map = ConceptMap.fetch("123")

    assert concept_map == ConceptMap(cm_123)

