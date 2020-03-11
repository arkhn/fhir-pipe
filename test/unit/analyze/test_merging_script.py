from unittest import mock
import pandas as pd

from fhirpipe.analyze.merging_script import MergingScript


def test_merging_script_init():
    merging_script = MergingScript("select_first_not_empty")

    assert merging_script.name == "select_first_not_empty"
    assert merging_script.script.__name__ == "select_first_not_empty"


def concat(*values):
    return "_".join(values)


@mock.patch("fhirpipe.analyze.merging_script.scripts.get_script", return_value=concat)
def test_merging_script_apply(_):
    merging_script = MergingScript("concat")

    df = pd.DataFrame(
        {
            "pk": [1, 2, 3, 4],
            "PATIENTS.NAME": ["alice", "bob", "carol", "denis"],
            "PATIENTS.SURNAME": ["a", "b", "c", "d"],
        }
    )

    static_values = ["djadja"]
    cols_to_merge = ["PATIENTS.NAME", "PATIENTS.SURNAME"]

    merged_col = merging_script.apply([df[col] for col in cols_to_merge], static_values, df["pk"])
    assert all(merged_col == ["alice_a_djadja", "bob_b_djadja", "carol_c_djadja", "denis_d_djadja"])
