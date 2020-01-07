def build_col_name(table, column, owner=None):
    return "{}{}.{}".format(owner + "." if owner is not None else "", table, column,)


def new_col_name(script_name, init_col):
    if isinstance(init_col, tuple):
        return script_name + "_" + "_".join(init_col[0]) + "_" + "_".join(init_col[1])
    return "_".join((script_name, init_col))


def get_table_name(name):
    """
    Extract the table_name from a column specification

    Example:
        Case 1
            OWNER.TABLE.COLUMN -> OWNER.TABLE
        Case 2
            TABLE.COLUMN -> TABLE
    """
    elems = name.split(".")
    if len(elems) == 3:
        return ".".join(name.split(".")[:2])
    elif len(elems) == 2:
        return name.split(".")[0]
    else:
        return None
