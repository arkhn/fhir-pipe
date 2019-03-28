import json

from fhirpipe.config import Config
from fhirpipe.parse.graph import DependencyGraph


config = Config("filesystem")
path = config.mapping + "/{}/templates/"


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


def get_table_col_name(name):
    if len(name.split(".")) != 3:
        raise TypeError("Name is not valid, should be <owner>.<table>.<col>.")
    return ".".join(name.split(".")[:])


def build_sql_query(project, resource, info="ICSF.PATIENT"):
    """
    Take a FHIR Resource (eg Patient) specification in input
    Output a sql query to fill this resource, and rules
    to combine (or squash) rows that embed a OneToMany relation
    :param project: name of the mapping project (eg CW)
    :param resource: the FHIR resource specification (as a dict)
    :param info:
    """
    table_name = get_table_name(info + ".*")

    # Get the info about the columns and joins to query
    cols, joins = dfs_find_sql_cols_joins(
        resource, source_table=table_name, project=project
    )

    print(cols)
    print(joins)

    # Format the sql arguments
    col_names = cols
    joins, dependency_graph = parse_joins(joins)
    sql_query = "SELECT {} FROM {} {}".format(
        ", ".join(col_names),
        table_name,
        " ".join(
            [
                "LEFT JOIN {} ON {}".format(join_table, join_bind)
                for join_table, join_bind in joins
            ]
        ),
    )
    # Reference for each table the columns which belongs to it: {table1: [col1, ...]}
    table_col_idx = {}
    for i, col in enumerate(col_names):
        table = get_table_name(col)
        if table not in table_col_idx:
            table_col_idx[table] = []
        table_col_idx[table].append(i)

    head_node = dependency_graph.get(table_name)
    squash_rules = build_squash_rule(head_node, table_col_idx)

    return sql_query, squash_rules, dependency_graph


def parse_joins(joins):
    """
    Transform a join info into SQL fragments and parse the graph of join dependency
    Input:
        [(<type_of_join>, "<owner>.<table>.<col>=<owner>.<join_table>.<join_col>"), ... ]
    Return:
        [(
            "<join_table>",
            "<table>.<col> = <join_table>.<join_col>"
        ), ... ],
        graph of dependency of type DependencyGraph
    """
    joins_elems = dict()
    graph = DependencyGraph()
    for join in joins:
        join_type, join_args = join
        # split the "<owner>.<table>.<col>=<owner>.<join_table>.<join_col>"
        join_parts = join_args.split("=")
        # Get <join_table>
        join_table = get_table_name(join_parts[1])
        # Get "<table>.<col> = <join_table>.<join_col>"
        join_bind = (
            get_table_col_name(join_parts[0])
            + " = "
            + get_table_col_name(join_parts[1])
        )
        joins_elems[join_table] = [join_table, join_bind]

        # Add the join in the join_graph
        source_table = get_table_name(join_parts[0])
        source_node = graph.get(source_table)
        join_node = graph.get(join_table)
        source_node.connect(join_node, join_type)
    return list(joins_elems.values()), graph


def dfs_find_sql_cols_joins(tree, source_table=None, project="CW"):
    """
    Run through the dict/tree of a Resource (and the references to templates)
    To find:
    - All columns name to select
    - All joins necessary to collect the data

    args:
        tree (dict): the fhir specification which has the structure of a tree
        node_type (default: None): type of the head node of the tree
        source_table (str): name of the source table, ie the table for which each row
            will create one instance of the considered resource
        project (str): the name of the project for load_template

    return:
        a dict containing all the columns referenced in the tree and all the joins
        to perform to access those columns

    TODO: change the dict return format to a tuple one
    """
    if isinstance(tree, dict):
        return find_cols_joins_in_object(tree, source_table, project)
    elif isinstance(tree, list) and len(tree) > 0:
        all_cols = []
        all_joins = []
        for t in tree:
            cols, joins = find_cols_joins_in_object(t, source_table, project)
            all_cols += cols
            all_joins += joins
        return all_cols, all_joins
    else:
        return [], []


def find_cols_joins_in_object(tree, source_table, project):
    """
    Inspect a tree specification of a FHIR mapping to find columns and joins
    :param tree: the mapping spec to explore
    :param node_type: type of the head node of the tree (useful for recursive calls)
    :param source_table: the reference SQL table for this FHIR resource
    :param project: ex: CW, (used for templating)
    :return: a dict {'cols': [...], 'joins': [...]}
    """
    # print(tree['id'])
    # Else if there are columns and scripts defined
    if "inputColumns" in tree.keys() and len(tree["inputColumns"]) > 0:
        joins = []
        column_names = []
        for col in tree["inputColumns"]:
            # If there is a join
            if "joins" in col.keys() and len(col["joins"]) > 0:
                for join in col["joins"]:
                    # Add the join
                    join_type = "OneToOne"  # TODO: infer type ?
                    join_args = "{}.{}.{}={}.{}.{}".format(
                        join["sourceOwner"],
                        join["sourceTable"],
                        join["sourceColumn"],
                        join["targetOwner"],
                        join["targetTable"],
                        join["targetColumn"],
                    )
                    joins += [(join_type, join_args)]

            # Check if table and column target are defined
            if col["table"] is not None and col["column"] is not None:
                column_name = "{}.{}.{}".format(
                    col["owner"], col["table"], col["column"]
                )
                column_names.append(column_name)
            # Else it's a static value and there is nothing to do

        return column_names, joins
    # Else, we have no join and no col referenced: just a json node (ex: name.given)
    else:
        cols, joins = dfs_find_sql_cols_joins(
            tree["attributes"], source_table, project=project
        )
        return cols, joins


def build_squash_rule(node, table_col_idx):
    """
    Using the dependency graph of the joins on the tables (accessed through the
    head node), regroup (using the id) the columns which should be squashed (ie
    those accessed through a OneToMany join)
    :param node: the node of the source table (which can be relative in recursive calls)
    :param table_col_idx: a dict [table_name]: list of idx of cols in the SQL response
        which come from this table
    :return: [
        (idx cols for source_table),
        [
            (idx cols for join OneToMany n1, []),
            (idx cols for join OneToMany n2, []),
            ...
        ]
    ]
    """
    # We refer the col indices of the table and all tables joined by a OneToOne
    unifying_col_idx = table_col_idx[node.name]
    for join_node in node.one_to_one:
        print(node.name, "---", join_node.name)
        join_cols, join_child_rules = build_squash_rule(join_node, table_col_idx)
        unifying_col_idx += join_cols
        if len(join_child_rules) > 0:
            print("ERROR", join_child_rules, "not handled")
    unifying_col_idx = tuple(sorted(unifying_col_idx))
    # Now parse the col indices for each table joined with a OneToMany
    child_rules = []
    for join_node in node.one_to_many:
        print(node.name, "-<=", join_node.name)
        child_rules.append(build_squash_rule(join_node, table_col_idx))
    return [unifying_col_idx, child_rules]