from unittest import mock
import pandas as pd

from fhirpipe.analyze.cleaning_script import CleaningScript


def test_cleaning_script_init():
    cleaning_script = CleaningScript("map_gender")

    assert cleaning_script.columns == []
    assert cleaning_script.name == "map_gender"
    assert cleaning_script.script.__name__ == "map_gender"


def capitalize(text):
    return text.upper()


@mock.patch("fhirpipe.analyze.cleaning_script.scripts.get_script", return_value=capitalize)
def test_cleaning_script_apply(_):
    cleaning_script = CleaningScript("capitalize")
    cleaning_script.columns.append("PATIENTS.NAME")
    cleaning_script.columns.append("PATIENTS.SURNAME")

    df = pd.DataFrame(
        {
            "pk": [1, 2, 3, 4],
            "PATIENTS.NAME": ["alice", "bob", "carol", "denis"],
            "PATIENTS.SURNAME": ["a", "b", "c", "d"],
        }
    )

    for col, values in cleaning_script.apply(df, "pk"):
        assert col in cleaning_script.columns
        assert all([x.isupper() for x in values])
