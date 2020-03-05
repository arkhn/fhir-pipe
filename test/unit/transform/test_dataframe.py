import pandas as pd
from unittest import mock

import fhirpipe.transform.dataframe as transform
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript


def test_squash_rows():
    df = pd.DataFrame(
        {
            "PATIENTS.NAME": ["bob", "bob", "alice", "bob"],
            "PATIENTS.ID": ["id1", "id1", "id2", "id3"],
            "ADMISSIONS.LANGUAGE": ["lang1", "lang2", "lang3", "lang4"],
            "ADMISSIONS.ID": ["id1", "id2", "id3", "id4"],
        },
    )
    squash_rules = ["PATIENTS", [["ADMISSIONS", []]]]

    actual = transform.squash_rows(df, squash_rules)
    # Sort to be sure actual and expected are in the same order
    actual = actual.sort_values(by="PATIENTS.ID").reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "PATIENTS.NAME": ["bob", "alice", "bob"],
            "PATIENTS.ID": ["id1", "id2", "id3"],
            "ADMISSIONS.LANGUAGE": [("lang1", "lang2"), ("lang3",), ("lang4",)],
            "ADMISSIONS.ID": [("id1", "id2"), ("id3",), ("id4",)],
        },
    )
    # Sort to be sure actual and expected are in the same order
    expected = expected.sort_values(by="PATIENTS.ID").reset_index(drop=True)

    assert actual.equals(expected)


def mock_get_script(*args):
    if len(args) == 1:
        return args[0] + "cleaned"
    else:
        return args[1] + args[2] + "merge"


@mock.patch("fhirpipe.analyze.cleaning_script.scripts.get_script", return_value=mock_get_script)
@mock.patch("fhirpipe.analyze.merging_script.scripts.get_script", return_value=mock_get_script)
def test_apply_scripts(_, __, fhir_concept_map_code, fhir_concept_map_gender):
    df = pd.DataFrame(
        {
            "NAME": ["alice", "bob", "charlie"],
            "ADDRESS": ["addr1", "addr2", "addr3"],
            "ID": ["id1", "id2", "id3"],
            "GENDER": ["M", "F", "F"],
            "CODE": ["ABC", "DEF", "GHI"],
        },
    )
    primary_key_column = "ID"

    # mock cleaning scripts
    clean1 = CleaningScript("clean1")
    clean1.columns.append("NAME")
    clean2 = CleaningScript("clean2")
    clean2.columns.extend(["NAME", "ADDRESS", "CODE"])
    cleaning_scripts = [clean1, clean2]

    # mock concept maps

    cm_gender = ConceptMap(fhir_concept_map_gender)
    cm_code = ConceptMap(fhir_concept_map_code)
    cm_gender.columns.append("GENDER")
    cm_code.columns.append("clean2_CODE")
    concept_maps = [cm_gender, cm_code]

    # mock merging scripts
    merge1 = MergingScript("merge")
    merge1.static_values.append("val")
    merge1.columns.extend(["ADDRESS", "ID"])
    merging_scripts = [merge1]

    transform.apply_scripts(df, cleaning_scripts, concept_maps, merging_scripts, primary_key_column)

    expected = pd.DataFrame(
        {
            "NAME": ["alice", "bob", "charlie"],
            "ADDRESS": ["addr1", "addr2", "addr3"],
            "ID": ["id1", "id2", "id3"],
            "GENDER": ["M", "F", "F"],
            "CODE": ["ABC", "DEF", "GHI"],
            "clean1_NAME": ["alicecleaned", "bobcleaned", "charliecleaned"],
            "clean2_NAME": ["alicecleaned", "bobcleaned", "charliecleaned"],
            "clean2_ADDRESS": ["addr1cleaned", "addr2cleaned", "addr3cleaned"],
            "clean2_CODE": ["ABCcleaned", "DEFcleaned", "GHIcleaned"],
            "id_cm_gender_GENDER": ["male", "female", "female"],
            "id_cm_code_clean2_CODE": ["abc", "def", "ghi"],
            "merge_ADDRESS_ID_val": ["id1valmerge", "id2valmerge", "id3valmerge"],
        },
    )

    assert df.equals(expected)
