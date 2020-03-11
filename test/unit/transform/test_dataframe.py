import pandas as pd
from unittest import mock

import fhirpipe.transform.dataframe as transform
from fhirpipe.analyze.attribute import Attribute
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript

from test.unit.conftest import mock_config, mock_api_get_maps


def mock_get_script(*args):
    if len(args) == 1:
        return args[0] + "cleaned"
    elif len(args) == 2:
        return args[0]
    else:
        return args[0] + args[1] + "merge"


@mock.patch("fhirpipe.analyze.cleaning_script.scripts.get_script", return_value=mock_get_script)
@mock.patch("fhirpipe.analyze.merging_script.scripts.get_script", return_value=mock_get_script)
@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_clean_data(_, __, fhir_concept_map_code, fhir_concept_map_gender):
    df = pd.DataFrame(
        {
            "PATIENTS_NAME": ["alice", "bob", "charlie"],
            "PATIENTS_ID": ["id1", "id2", "id3"],
            "PATIENTS_ID2": ["id21", "id22", "id23"],
            "ADMISSIONS_LANGUAGE": ["M", "F", "F"],
            "ADMISSIONS_CODE": ["ABC", "DEF", "GHI"],
        },
    )
    attr_name = Attribute(
        "name", columns=[SqlColumn("PATIENTS", "NAME", cleaning_script=CleaningScript("clean1"),)]
    )
    attr_id = Attribute(
        "id",
        columns=[SqlColumn("PATIENTS", "ID"), SqlColumn("PATIENTS", "ID2")],
        static_inputs=["null"],
        merging_script=MergingScript("merge"),
    )
    attr_gender = Attribute(
        "language",
        columns=[SqlColumn("ADMISSIONS", "LANGUAGE", concept_map=ConceptMap("id_cm_gender"))],
        static_inputs=["val"],
    )
    attr_code = Attribute(
        "code",
        columns=[
            SqlColumn(
                "ADMISSIONS",
                "CODE",
                cleaning_script=CleaningScript("clean2"),
                concept_map=ConceptMap("id_cm_code"),
            )
        ],
    )
    attributes = [attr_name, attr_id, attr_gender, attr_code]

    primary_key_column = SqlColumn("PATIENTS", "ID")

    cleaned_df = transform.clean_data(df, attributes, primary_key_column)

    expected = pd.DataFrame(
        {
            attr_name: ["alicecleaned", "bobcleaned", "charliecleaned"],
            attr_id: ["id1id21merge", "id2id22merge", "id3id23merge"],
            attr_gender: ["male", "female", "female"],
            attr_code: ["abc", "def", "ghi"],
        },
    )

    assert cleaned_df.equals(expected)


def test_squash_rows():
    attr_name = Attribute("name", columns=[SqlColumn("PATIENTS", "NAME")])
    attr_id = Attribute("id", columns=[SqlColumn("PATIENTS", "ID")])
    attr_language = Attribute("language", columns=[SqlColumn("ADMISSIONS", "LANGUAGE")])
    attr_admid = Attribute("admid", columns=[SqlColumn("ADMISSIONS", "ID")])
    df = pd.DataFrame(
        {
            attr_name: ["bob", "bob", "alice", "bob"],
            attr_id: ["id1", "id1", "id2", "id3"],
            attr_language: ["lang1", "lang2", "lang3", "lang4"],
            attr_admid: ["id1", "id2", "id3", "id4"],
        },
    )
    squash_rules = ["PATIENTS", [["ADMISSIONS", []]]]

    actual = transform.squash_rows(df, squash_rules)
    # Sort to be sure actual and expected are in the same order
    actual = actual.sort_values(by=attr_id).reset_index(drop=True)

    expected = pd.DataFrame(
        {
            attr_name: ["bob", "alice", "bob"],
            attr_id: ["id1", "id2", "id3"],
            attr_language: [("lang1", "lang2"), ("lang3",), ("lang4",)],
            attr_admid: [("id1", "id2"), ("id3",), ("id4",)],
        },
    )
    # Sort to be sure actual and expected are in the same order
    expected = expected.sort_values(by=attr_id).reset_index(drop=True)

    assert actual.equals(expected)
