import pytest
from unittest import mock

from fhirpipe.analyze.concept_map import ConceptMap

from test.unit.conftest import mock_config, mock_api_get_maps


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
def test_fetch_concept_map(fhir_concept_map_gender):
    concept_map = ConceptMap.fetch(fhir_concept_map_gender["title"])

    assert concept_map == ConceptMap(fhir_concept_map_gender)

    # should raise if not found
    with pytest.raises(Exception, match="Error while fetching concept map nope: not found."):
        ConceptMap.fetch("nope")
