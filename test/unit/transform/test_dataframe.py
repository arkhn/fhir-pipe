import pandas as pd
from unittest import mock

import fhirpipe.transform.dataframe as transform


def test_squash_rows():
    df = pd.DataFrame(
        {
            "PATIENTS.NAME": ["bob", "bob", "alice", "bob"],
            "PATIENTS.ID": ["id1", "id1", "id2", "id3"],
            "ADMISSIONS.LANGUAGE": ["lang1", "lang2", "lang3", "lang4"],
            "ADMISSIONS.ID": ["id1", "id2", "id3", "id4"],
        }
    )
    squash_rules = ["PATIENTS", [["ADMISSIONS", []]]]

    actual = transform.squash_rows(df, squash_rules)
    # Sort to be sure actual and expected are in the same order
    actual = actual.sort_values(by="PATIENTS.ID").reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "PATIENTS.NAME": ["bob", "alice", "bob"],
            "PATIENTS.ID": ["id1", "id2", "id3"],
            "ADMISSIONS.LANGUAGE-ADMISSIONS.ID": [
                [["lang1", "id1"], ["lang2", "id2"]],
                ["lang3", "id3"],
                ["lang4", "id4"],
            ],
        }
    )
    # Sort to be sure actual and expected are in the same order
    expected = expected.sort_values(by="PATIENTS.ID").reset_index(drop=True)

    assert actual.to_json() == expected.to_json()


def mock_get_script(*args):
    if len(args) == 1:
        return args[0] + "cleaned"
    else:
        return args[1] + args[2] + "merge"


@mock.patch(
    "fhirpipe.transform.dataframe.scripts.get_script", return_value=mock_get_script
)
def test_apply_scripts(get_script):
    df = pd.DataFrame(
        {
            "NAME": ["alice", "bob", "charlie"],
            "ADDRESS": ["addr1", "addr2", "addr3"],
            "ID": ["id1", "id2", "id3"],
        }
    )
    cleaning = {"clean1": ["NAME"], "clean2": ["ADDRESS"], "clean3": ["ID"]}
    merging = {"merge": [(["ADDRESS", "ID"], ["val"])]}

    transform.apply_scripts(df, cleaning, merging)

    expected = pd.DataFrame(
        {
            "NAME": ["alicecleaned", "bobcleaned", "charliecleaned"],
            "ADDRESS": [
                "id1cleanedvalmerge",
                "id2cleanedvalmerge",
                "id3cleanedvalmerge",
            ],
        }
    )

    assert df.equals(expected)
