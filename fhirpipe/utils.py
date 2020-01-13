import re
from collections import defaultdict


def build_col_name(table, column, owner=None):
    if owner:
        return f"{owner}.{table}.{column}"
    else:
        return f"{table}.{column}"


def new_col_name(script_name, init_col):
    if isinstance(init_col, tuple):
        return f"{script_name}_{'_'.join(init_col[0])}_{'_'.join(init_col[1])}"
    return f"{script_name}_{init_col}"


column_pattern = re.compile(r"(?:\w+\.)?(\w+)\.\w+")


def get_table_name(name):
    """
    Extract the table_name from a column specification

    Example:
        Case 1
            OWNER.TABLE.COLUMN -> OWNER.TABLE
        Case 2
            TABLE.COLUMN -> TABLE
    """
    return re.search(column_pattern, name).group(1)


def dict_concat(dict_1, dict_2):
    for key, val in dict_2.items():
        dict_1[key] += val


def build_join_graph(joins):
    """
    Transform a join info into SQL fragments and parse the graph of join dependency
    Input:
        {("<owner>.<table>.<col>", "<owner>.<join_table>.<join_col>"), ... }
    Return:
        {
            "<table>": ["<join_table 1>", "<join_table 2>", ...],
            ...
        }
    """
    graph = defaultdict(list)
    for join in joins:
        join_source, join_target = join

        # Get table names
        target_table = get_table_name(join_target)
        source_table = get_table_name(join_source)

        # Add the join in the join_graph
        graph[source_table].append(target_table)

    return graph
