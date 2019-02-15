import json
import yaml
import re
import logging
from os import listdir
from os.path import isfile, join

from arkhn import scripts
from arkhn.parser import checks
from arkhn.config import Config


config = Config("filesystem")
path = config.mapping + "/{}/templates/"


def _is_empty(value):
    return value is None or value == "NaN" or value == ""


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


def remove_owner(name):
    """
    Input:
        "(?:<owner>.)<table>.<col>"
    Return:
        "<table>.<col>"
    """
    if len(name.split(".")) == 3:
        return get_table_col_name(name)
    else:
        return name


def add_table_name(col, table):
    """
    Input:
        "<col>", table
    Return:
        "<table>.<col>"
    """
    if len(col.split(".")) == 1:
        return "{}.{}".format(table, col)
    else:
        logging.warning("Useless add_table_name for {}".format(col))
        return col


def parse_name_type(name_type):
    """
    arg:
        name_type (str): keyname<(list::)type>
    Return:
        (tuple) key_name, type, is_list
    """
    r = re.compile(r"^([^<]*)(?:<(.*)>)?")
    name, node_type = r.findall(name_type)[0]

    is_list = node_type.startswith("list")
    if len(node_type.split("::")) > 1:
        node_type = node_type.split("::")[1]
    elif is_list:
        node_type = None
    return name, node_type, is_list


def parse_type(node_type):
    """

    """
    is_list = node_type.startswith("list")
    if len(node_type.split("::")) > 1:
        node_type = node_type.split("::")[1]
    elif is_list:
        node_type = None
    return node_type, is_list


def is_node_type_templatable(project, type_name):
    """
    Check that the node_type is compatible with templating
    """
    full_path = path.format(project)
    datatypes = [
        filename.split(".")[0]
        for filename in listdir(full_path)
        if isfile(join(full_path, filename))
    ]
    return type_name in datatypes


def build_sql_query(project, resource, info='ICSF.PATIENT'):
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
    cols, joins = dfs_find_sql_cols_joins(resource, source_table=table_name, project=project)

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
    # Now build the col indices for each table joined with a OneToMany
    child_rules = []
    for join_node in node.one_to_many:
        print(node.name, "-<=", join_node.name)
        child_rules.append(build_squash_rule(join_node, table_col_idx))
    return [unifying_col_idx, child_rules]


class Table:
    """
    Node in the graph of dependency. Represents a table, and attributes
    one_to_one, one_to_many link to other nodes / tables.
    """

    def __init__(self, table_name):
        self.name = table_name
        self.one_to_one = []
        self.one_to_many = []

    def __repr__(self):
        string = "[{} O2O:({}) O2M:({})]".format(
            self.name,
            ",".join([j.name for j in self.one_to_one]),
            ",".join([j.name for j in self.one_to_many]),
        )
        return string

    def connect(self, table, join_type):
        """
        Declare a join
        :param table: end table of the join
        :param join_type: type of join
        """
        if join_type == "OneToOne":
            if table not in self.one_to_one:
                self.one_to_one.append(table)
        elif join_type == "OneToMany":
            if table not in self.one_to_many:
                self.one_to_many.append(table)
        else:
            raise TypeError("Join type is not valid:", join_type)

    def connected(self, table):
        return table in (self.one_to_one + self.one_to_many)


class DependencyGraph:
    """
    Graph of dependency to show all joins between tables
    """

    def __init__(self):
        self.nodes = {}

    def has(self, table):
        return table in self.nodes

    def add(self, table):
        node = Table(table)
        self.nodes[table] = node

    def get(self, table):
        if not self.has(table):
            self.add(table)
        return self.nodes[table]

    def __repr__(self):
        out = "Dependency Graph\n"
        for name, node in self.nodes.items():
            out += "{}: {}\n".format(name, node.__repr__())
        return out


def parse_joins(joins):
    """
    Transform a join info into SQL fragments and build the graph of join dependency
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


# Cache all templates to save read disk operations
templates_cache = {}


def load_template(project, data_type, template_id):
    """
    Return the dict template of a resource with id template_id
    args:
        project: ex CW
        data_type: the DataType (see FHIR DataType spec) (ex: HumanName, Identifier)
        template_id:
    """
    full_path = path.format(project)
    file_path = full_path + data_type + ".yml"

    # specify an id to retrieve the template
    ref_id = "{}>{}".format(file_path, template_id)
    if ref_id in templates_cache:
        return templates_cache[ref_id].copy()

    with open(file_path, "r") as stream:
        try:
            data = yaml.load(stream)
            template = data[data_type][template_id]
            templates_cache[ref_id] = template.copy()
            return template
        except yaml.YAMLError as exc:
            print(exc)
    return None


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
            if "joins" in col.keys() and len(col['joins']) > 0:
                for join in col["joins"]:
                    # Add the join
                    join_type = "OneToOne"  # TODO: infer type ?
                    join_args = "{}.{}.{}={}.{}.{}".format(
                        join['sourceOwner'],
                        join['sourceTable'],
                        join['sourceColumn'],
                        join['targetOwner'],
                        join['targetTable'],
                        join['targetColumn'],
                    )
                    joins += [(join_type, join_args)]

            # Check if table and column target are defined
            if col['table'] is not None and col['column'] is not None:
                column_name = "{}.{}.{}".format(
                    col['owner'],
                    col['table'],
                    col['column']
                )
                column_names.append(column_name)
            # Else it's a static value and there is nothing to do

        # cols = _list(col)
        # cols = [remove_owner(col) for col in cols]
        # if source_table is not None:
        #     cols = [add_table_name(col, source_table) for col in cols]
        # print(column_names)
        return column_names, joins
    # Else, we have no join and no col referenced: just a json node (ex: name.given)
    else:
        cols, joins = dfs_find_sql_cols_joins(
            tree['attributes'], source_table, project=project
        )
        return cols, joins


def _list(obj):
    """
    Cast into a list if not a list already
    """
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


def _unlist(list_obj):
    """
    Return first obj if list with a single elem, else return list
    """
    return list_obj[0] if len(list_obj) == 1 else list_obj


def get_script_arity(cols, scripts):
    """
    Return the number of arguments per script
    """
    if isinstance(cols, str or isinstance(scripts, str)):
        return 1
    if len(cols) == len(scripts):
        return [get_script_arity(col, script) for col, script in zip(cols, scripts)]
    elif len(scripts) == 1:
        return len(cols)
    else:
        raise TypeError(
            "Cant match {} cols with {} scripts".format(len(cols), len(scripts))
        )


def dfs_create_fhir(d, tree, row):
    """
        For each instance of a Resource,
        Run through the dict/tree of a Resource (and the references to templates)
        And build a similar dict, where we replace all occurrences of inputColumns
        with the result of the query,
        Processed by the appropriate script.

        args:
            d: the fhir structure we build
            tree: the FHIR spec mapping from graphql
            row: one row of the result of the SQL query

        return:
            None
    """
    # if there are columns specified
    if "inputColumns" in tree.keys() and len(tree["inputColumns"]) > 0:
        l = []
        for col in tree['inputColumns']:
            if col['table'] is not None and col['column'] is not None:
                script_name = col['script']
                value = row.pop(0)
                if script_name is not None:
                    value = scripts.get_script(script_name)(value)
                l.append(value)
            else:
                l.append(col['staticValue'])

        if tree['type'].startswith('list'):
            d[tree['name']] = l
        else:
            d[tree['name']] = ''.join(l)
    else:  # else iterate recursively
        if tree['type'].startswith('list'):
            d[tree['name']] = list()
            for a in tree['attributes']:
                if len(row) > 0 and isinstance(row[0], list):
                    join_rows = row.pop(0)
                    for join_row in join_rows:
                        d2 = dict()
                        dfs_create_fhir(d2, a, list(join_row))
                        d[tree['name']].append(d2)
                else:
                    d2 = dict()
                    dfs_create_fhir(d2, a, row)
                    d[tree['name']].append(d2)
        elif tree['isProfile']:
            for a in tree['attributes']:
                dfs_create_fhir(d, a, row)
        else:
            d[tree['name']] = dict()
            for a in tree['attributes']:
                dfs_create_fhir(d[tree['name']], a, row)


def clean_fhir(tree):
    """
    Remove all empty leaves and branches of the fhir object
    (ie: None, empty list, or nested empty things)
    :param tree: dirty fhir object
    :return: clean fhir object
    """
    if isinstance(tree, dict):
        weight = 0
        clean_tree = {}
        for k, t in tree.items():
            clean_t, w = clean_fhir(t)
            if w > 0:
                clean_tree[k] = clean_t
                weight += w
        return clean_tree, weight

    elif isinstance(tree, list):
        weight = 0
        clean_tree = []
        for t in tree:
            clean_t, w = clean_fhir(t)
            if w > 0:
                clean_tree.append(clean_t)
                weight += w
        return clean_tree, weight
    else:
        if _is_empty(tree):
            return tree, 0
        else:
            return tree, 1


def write_to_file(rows, filename):
    with open(filename, "w+") as f:
        for row in rows:
            f.write("{}\n".format(json.dumps(row)))
