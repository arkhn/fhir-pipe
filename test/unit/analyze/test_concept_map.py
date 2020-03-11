import pytest
from unittest import mock
import pandas as pd

from fhirpipe.analyze.concept_map import ConceptMap

from test.unit.conftest import mock_config, mock_api_get_maps


@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_fetch_concept_map(fhir_concept_map_gender):
    concept_map = ConceptMap.fetch(fhir_concept_map_gender["id"])

    assert concept_map == fhir_concept_map_gender

    # should raise if not found
    with pytest.raises(Exception, match="Error while fetching concept map nope: not found."):
        ConceptMap.fetch("nope")


def test_convert_to_dict():
    fhir_concept_map = {
        "id": "test_123",
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

    mapping = ConceptMap.convert_to_dict(fhir_concept_map)

    assert mapping == {
        "src_code": "trgt_code",
        "code1": "code2",
        "11": "12",
        "21": "22",
        "31": "32",
    }


@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_concept_map_apply(fhir_concept_map_gender):
    concept_map = ConceptMap(fhir_concept_map_gender["id"])

    df = pd.DataFrame({"pk": [1, 2, 3, 4], "PATIENTS.GENDER": ["M", "F", "M", "F"]})

    mapped_col = concept_map.apply(df["PATIENTS.GENDER"], "pk")

    assert all(mapped_col == ["male", "female", "male", "female"])
