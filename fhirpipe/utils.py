import re


def build_col_name(table, column, owner=None):
    if owner:
        return f"{owner}.{table}.{column}"
    else:
        return f"{table}.{column}"


def new_col_name(script_name, init_col):
    if isinstance(init_col, tuple):
        return f"{script_name}_{'_'.join(init_col[0])}_{'_'.join(init_col[1])}"
    return f"{script_name}_{init_col}"


def get_table_name(name):
    """
    Extract the table_name from a column specification

    Example:
        Case 1
            OWNER.TABLE.COLUMN -> OWNER.TABLE
        Case 2
            TABLE.COLUMN -> TABLE
    """
    column_pattern = re.compile(r"(?:\w+\.)?(\w+)\.\w+")
    return re.search(column_pattern, name).group(1)


def dict_concat(dict_1, dict_2):
    for key, val in dict_2.items():
        dict_1[key] += val
