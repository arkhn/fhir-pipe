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
@mock.patch("fhirpipe.analyze.concept_map.fhirpipe.global_config", mock_config)
@mock.patch("fhirpipe.analyze.concept_map.requests.get", mock_api_get_maps)
def test_clean_data(_, fhir_concept_map_code, fhir_concept_map_gender):
    df = pd.DataFrame(
        {
            "PATIENTS_NAME": ["alice", "bob", "charlie"],
            "PATIENTS_ID": ["id1", "id2", "id3"],
            "PATIENTS_ID2": ["id21", "id22", "id23"],
            "ADMISSIONS_LANGUAGE": ["M", "F", "F"],
            "ADMISSIONS_ID": ["ABC", "DEF", "GHI"],
        },
    )
    attr_name = Attribute(
        "name", columns=[SqlColumn("PATIENTS", "NAME", cleaning_script=CleaningScript("clean1"),)]
    )
    attr_id = Attribute(
        "id",
        columns=[SqlColumn("PATIENTS", "ID"), SqlColumn("PATIENTS", "ID2")],
        static_inputs=["null"],
    )
    attr_language = Attribute(
        "language",
        columns=[SqlColumn("ADMISSIONS", "LANGUAGE", concept_map=ConceptMap("id_cm_gender"))],
        static_inputs=["val"],
    )
    attr_admid = Attribute(
        "code",
        columns=[
            SqlColumn(
                "ADMISSIONS",
                "ID",
                cleaning_script=CleaningScript("clean2"),
                concept_map=ConceptMap("id_cm_code"),
            )
        ],
    )
    attributes = [attr_name, attr_id, attr_language, attr_admid]
    primary_key_column = SqlColumn("PATIENTS", "ID")

    cleaned_df = transform.clean_dataframe(df, attributes, primary_key_column)

    df_columns = pd.MultiIndex.from_tuples(
        [
            (attr_name, ("PATIENTS_NAME", "PATIENTS")),
            (attr_id, ("PATIENTS_ID", "PATIENTS")),
            (attr_id, ("PATIENTS_ID2", "PATIENTS")),
            (attr_language, ("ADMISSIONS_LANGUAGE", "ADMISSIONS")),
            (attr_admid, ("ADMISSIONS_ID", "ADMISSIONS")),
            ("pk", ("PATIENTS_ID", "PATIENTS")),
        ]
    )

    expected = pd.DataFrame(
        {
            df_columns[0]: ["alicecleaned", "bobcleaned", "charliecleaned"],
            df_columns[1]: ["id1", "id2", "id3"],
            df_columns[2]: ["id21", "id22", "id23"],
            df_columns[3]: ["male", "female", "female"],
            df_columns[4]: ["abc", "def", "ghi"],
            df_columns[5]: ["id1", "id2", "id3"],
        },
    )

    assert cleaned_df.equals(expected)


def test_squash_rows():
    attr_name = Attribute("name", columns=[SqlColumn("PATIENTS", "NAME")])
    attr_id = Attribute("id", columns=[SqlColumn("PATIENTS", "ID")])
    attr_language = Attribute("language", columns=[SqlColumn("ADMISSIONS", "LANGUAGE")])
    attr_admid = Attribute("admid", columns=[SqlColumn("ADMISSIONS", "ID")])

    df_columns = pd.MultiIndex.from_tuples(
        [
            (attr_name, ("PATIENTS_NAME", "PATIENTS")),
            (attr_id, ("PATIENTS_ID", "PATIENTS")),
            (attr_language, ("ADMISSIONS_LANGUAGE", "ADMISSIONS")),
            (attr_admid, ("ADMISSIONS_ID", "ADMISSIONS")),
        ]
    )

    df = pd.DataFrame(
        {
            df_columns[0]: ["bob", "bob", "alice", "bob"],
            df_columns[1]: ["id1", "id1", "id2", "id3"],
            df_columns[2]: ["lang1", "lang2", "lang3", "lang4"],
            df_columns[3]: ["id1", "id2", "id3", "id4"],
        },
    )
    squash_rules = ["PATIENTS", [["ADMISSIONS", []]]]

    actual = transform.squash_rows(df, squash_rules)
    # Sort to be sure actual and expected are in the same order
    actual = actual.sort_values(by=df_columns[1]).reset_index(drop=True)

    expected = pd.DataFrame(
        {
            df_columns[0]: ["bob", "alice", "bob"],
            df_columns[1]: ["id1", "id2", "id3"],
            df_columns[2]: [("lang1", "lang2"), ("lang3",), ("lang4",)],
            df_columns[3]: [("id1", "id2"), ("id3",), ("id4",)],
        },
    )
    # Sort to be sure actual and expected are in the same order
    expected = expected.sort_values(by=df_columns[1]).reset_index(drop=True)

    assert actual.equals(expected)


@mock.patch("fhirpipe.analyze.merging_script.scripts.get_script", return_value=mock_get_script)
def test_merge_dataframe(_):
    attr_name = Attribute("name", columns=[SqlColumn("PATIENTS", "NAME")])
    attr_id = Attribute(
        "id",
        columns=[SqlColumn("PATIENTS", "ID"), SqlColumn("PATIENTS", "ID2")],
        static_inputs=["unknown"],
        merging_script=MergingScript("merge"),
    )
    attr_language = Attribute("language", columns=[SqlColumn("ADMISSIONS", "LANGUAGE")])
    attr_admid = Attribute("admid", columns=[SqlColumn("ADMISSIONS", "ID")])

    df_columns = pd.MultiIndex.from_tuples(
        [
            (attr_name, ("PATIENTS_NAME", "PATIENTS")),
            (attr_id, ("PATIENTS_ID", "PATIENTS")),
            (attr_id, ("PATIENTS_ID2", "PATIENTS")),
            (attr_language, ("ADMISSIONS_LANGUAGE", "ADMISSIONS")),
            (attr_admid, ("ADMISSIONS_ID", "ADMISSIONS")),
            ("pk", ("PATIENTS_ID", "PATIENTS")),
        ]
    )

    df = pd.DataFrame(
        {
            df_columns[0]: ["bob", "bob", "alice", "bob"],
            df_columns[1]: ["id1", "id1", "id2", "id3"],
            df_columns[2]: ["id21", "id21", "id22", "id23"],
            df_columns[3]: ["lang1", "lang2", "lang3", "lang4"],
            df_columns[4]: ["hadmid1", "hadmid2", "hadmid3", "hadmid4"],
            df_columns[5]: ["id1", "id2", "id3", "id4"],
        },
    )
    attributes = [attr_name, attr_id, attr_language, attr_admid]
    primary_key_column = SqlColumn("PATIENTS", "ID")

    actual = transform.merge_dataframe(df, attributes, primary_key_column)

    expected = pd.DataFrame(
        {
            attr_name: ["bob", "bob", "alice", "bob"],
            attr_id: ["id1id21merge", "id1id21merge", "id2id22merge", "id3id23merge"],
            attr_language: ["lang1", "lang2", "lang3", "lang4"],
            attr_admid: ["hadmid1", "hadmid2", "hadmid3", "hadmid4"],
        },
    )

    assert actual.equals(expected)
