import fhirpipe.utils as utils


def test_new_col_name():
    result = utils.new_col_name("clean", "col")
    assert result == "clean_col"

    result = utils.new_col_name("merge", (["col1", "col2"], ["static1", "static2"]))
    assert result == "merge_col1_col2_static1_static2"


def test_get_table_name():
    result = utils.get_table_name("owner.table.col")
    assert result == "owner.table"

    result = utils.get_table_name("table.col")
    assert result == "table"
