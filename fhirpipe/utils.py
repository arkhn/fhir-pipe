def build_col_name(table, column, owner=None):
    table = table.strip()
    column = column.strip()
    owner = owner.strip() if owner is not None else owner
    if owner:
        return f"{owner}.{table}.{column}"
    else:
        return f"{table}.{column}"


def new_col_name(script_name, init_col):
    if isinstance(init_col, tuple):
        if init_col[1]:
            return f"{script_name}_{'_'.join(init_col[0])}_{'_'.join(init_col[1])}"
        else:
            return f"{script_name}_{'_'.join(init_col[0])}"
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
    return name.rsplit(".", 1)[0]
