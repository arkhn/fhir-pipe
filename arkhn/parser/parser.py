import json
import yaml
import re
import logging
from os import listdir
from os.path import isfile, join

from arkhn import scripts
from arkhn.parser import checks


path = '../../fhir-mapping/{}/templates/'


def _is_empty(value):
    return value is None or value == 'NaN' or value == ''


def get_table_name(name):
    elems = name.split('.')
    if len(elems) == 3:
        return name.split('.')[1]
    elif len(elems) == 2:
        return name.split('.')[0]
    else:
        return None


def get_table_col_name(name):
    if len(name.split('.')) != 3:
        raise TypeError('Name is not valid, should be <owner>.<table>.<col>.')
    return '.'.join(name.split('.')[1:])


def remove_owner(name):
    """
    Input:
        "(?:<owner>.)<table>.<col>"
    Return:
        "<table>.<col>"
    """
    if len(name.split('.')) == 3:
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
    if len(col.split('.')) == 1:
        return '{}.{}'.format(table, col)
    else:
        logging.warning('Useless add_table_name for {}'.format(col))
        return col


def parse_name_type(name_type):
    """
    Input:
        keyname<(list::)type>
    Return:
        keyname, type, is_list
    """
    r = re.compile(r'^([^<]*)(?:<(.*)>)?')
    name, node_type = r.findall(name_type)[0]

    is_list = node_type.startswith('list')
    if len(node_type.split('::')) > 1:
        node_type = node_type.split('::')[1]
    elif is_list:
        node_type = None
    return name, node_type, is_list


def is_node_type_templatable(project, type_name):
    """
    Check that the node_type is compatible with templating
    """
    full_path = path.format(project)
    datatypes = [
        filename.split('.')[0]
        for filename in listdir(full_path)
        if isfile(join(full_path, filename))
    ]
    return type_name in datatypes


def build_sql_query(project, resource, info):
    """
    Take a Resource (eg Patient) scheme in input
    Output a sql query to fill this resource, and rules
    to combine (or squash) rows that embed a OneToMany relation
    :param project: Name of the mapping project (eg CW)
    :param resource: Name of the FHIR resource to fill
    :param info: a dict with the source_table and optionally more
    """
    table_name = get_table_name(info['source_table'] + '.*')

    # Get the info about the columns and joins to query
    d = dfs_find_sql_cols_joins(resource, source_table=table_name, project=project)
    # Format the sql arguments
    col_names = d['cols']
    joins, dependency_graph = parse_joins(d['joins'])
    sql_query = 'SELECT {} FROM {} {};'.format(
        ', '.join(col_names),
        table_name,
        ' '.join([
            'LEFT JOIN {} ON {}'.format(join_table, join_bind)
            for join_table, join_bind in joins
        ])
    )
    # Reference for each table the columns which belongs to it.
    table_col_idx = {}
    for i, col in enumerate(col_names):
        table = get_table_name(col)
        if table not in table_col_idx:
            table_col_idx[table] = []
        table_col_idx[table].append(i)

    head_node = dependency_graph.get(table_name)
    squash_rules = build_squash_rule(head_node, dependency_graph, table_col_idx)

    return sql_query, squash_rules, dependency_graph


def build_squash_rule(node, graph, table_col_idx):
    """
    Using the dependency graph of the joins on the tables, regroup (using the id)
    the columns which should be squashed
    :param node: the node of the source table
    :param graph: the dependency graph with all the joins
    :param table_col_idx: a dict [table_name]: list of idx of cols in the SQL response which
      come from this table
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
        print(node.name, '---', join_node.name)
        join_cols, join_child_rules = build_squash_rule(join_node, graph, table_col_idx)
        unifying_col_idx += join_cols
        if len(join_child_rules) > 0:
            print('ERROR', join_child_rules, 'not handled')
    unifying_col_idx = tuple(sorted(unifying_col_idx))
    # Now build the col indices for each table binded with a OneToMany
    child_rules = []
    for join_node in node.one_to_many:
        print(node.name, '-<=', join_node.name)
        child_rules.append(build_squash_rule(join_node, graph, table_col_idx))
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
        string = '[{} O2O:({}) O2M:({})]'.format(
            self.name,
            ','.join([j.name for j in self.one_to_one]),
            ','.join([j.name for j in self.one_to_many])
        )
        return string

    def connect(self, table, join_type):
        """
        Declare a join
        :param table: end table of the join
        :param join_type: type of join
        """
        if join_type == 'OneToOne':
            if table not in self.one_to_one:
                self.one_to_one.append(table)
        elif join_type == 'OneToMany':
            if table not in self.one_to_many:
                self.one_to_many.append(table)
        else:
            raise TypeError('Join type is not valid:', join_type)

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
        graph of dependency
    """
    joins_elems = dict()
    graph = DependencyGraph()
    for join in joins:
        join_type, join_args = join
        # split the "<owner>.<table>.<col>=<owner>.<join_table>.<join_col>"
        join_parts = join_args.split('=')
        # Get <join_table>
        join_table = get_table_name(join_parts[1])
        # Get "<table>.<col> = <join_table>.<join_col>"
        join_bind = get_table_col_name(join_parts[0]) + ' = ' + get_table_col_name(join_parts[1])
        joins_elems[join_table] = [join_table, join_bind]

        # Add the join in the join_graph
        source_table = get_table_name(join_parts[0])
        source_node = graph.get(source_table)
        join_node = graph.get(join_table)
        source_node.connect(join_node, join_type)
    return list(joins_elems.values()), graph

# Cache all templates
templates_cache = {}


def load_template(project, data_type, template_id):
    """
    Return the dict template of a resource with id template_id
    """
    full_path = path.format(project)
    file_path = full_path + data_type + '.yml'

    ref_id = '{}>{}'.format(file_path, template_id)
    if ref_id in templates_cache:
        return templates_cache[ref_id].copy()

    with open(file_path, 'r') as stream:
        try:
            data = yaml.load(stream)
            template = data[data_type][template_id]
            templates_cache[ref_id] = template.copy()
            return template
        except yaml.YAMLError as exc:
            print(exc)
    return None


def dfs_find_sql_cols_joins(tree, node_type=None, source_table=None, project='CW'):
    """
        Run through the dict/tree of a Resource (and the references to templates)
        To find:
        - All columns name to select
        - All joins necessary to collect the data
        :param project:
    """
    if isinstance(tree, dict):
        return find_cols_joins_in_object(tree, node_type, source_table, project)
    elif isinstance(tree, list) and len(tree) > 0:
        response = {'cols': [], 'joins': []}
        for t in tree:
            d = find_cols_joins_in_object(t, node_type, source_table, project)
            response['cols'] += d['cols']
            response['joins'] += d['joins']
        return response
    else:
        return {'cols': [], 'joins': []}


def find_cols_joins_in_object(tree, node_type, source_table, project):
    children = tree.keys()
    joins = []
    # If there is a join
    if '_join' in tree.keys():
        join_info = tree['_join']
        # Add the join
        join = (join_info['_type'], _unlist(join_info['_args']))
        joins = _list(join)

    # If there is a template
    if '_template_id' in tree.keys():
        # Load the referenced template
        template_ids = tree['_template_id']
        assert is_node_type_templatable(project, node_type), "Can't have a template for type {}".format(node_type)
        template_ids = _list(template_ids)
        template_cols = []
        template_joins = []
        for template_id in template_ids:
            template = load_template(project, node_type, template_id)
            template_d = dfs_find_sql_cols_joins(template, node_type, project=project)
            template_cols += template_d['cols']
            template_joins += template_d['joins']
        return {'cols': [] + template_cols, 'joins': joins + template_joins}
    # Else if there are columns and scripts defined
    elif '_col' in tree.keys() and '_script' in tree.keys():
        col = tree['_col']
        cols = _list(col)
        cols = [remove_owner(col) for col in cols]
        if source_table is not None:
            cols = [add_table_name(col, source_table) for col in cols]
        return {'cols': cols, 'joins': joins}
    # Else, we have no join and no col referenced: just a json node (ex: name.given)
    else:
        cols = []
        joins = []
        for child in children:
            name, node_type, is_list = parse_name_type(child)
            d = dfs_find_sql_cols_joins(tree[child], node_type, source_table, project=project)
            child_cols = d['cols']
            child_joins = d['joins']
            cols += child_cols
            joins += child_joins
        return {'cols': cols, 'joins': joins}


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
        raise TypeError("Cant match {} cols with {} scripts".format(len(cols), len(scripts)))


def dfs_create_fhir(project, tree, row, node_type=None):
    """
    For each instance of a Resource,
    Run again through the dict/tree of a Resource (and the references to templates)
    And build a similar dict, where we replace all occurrences of _col with the result of the query,
    Processed by the appropriate _script.
    Return a dict which is in the partial fhir format.
    """
    if isinstance(tree, dict):
        children = tree.keys()

        # If there is a template for the join
        if '_template_id' in tree.keys():
            # Load the referenced template
            template_ids = _list(tree['_template_id'])

            response = []
            for template_id in template_ids:
                template = load_template(project, node_type, template_id)
                resp = dfs_create_fhir(project, template, row, node_type)
                response.append(resp)
            return _unlist(response)
        # Else if there are columns and scripts defined
        elif '_col' in tree.keys() and '_script' in tree.keys():
            script_names = _list(tree['_script'])
            col_names = _list(tree['_col'])
            script_arities = _list(get_script_arity(col_names, script_names))
            values = []
            for name, arity in zip(script_names, script_arities):
                # Row.pop(0) pops out the first element in row
                args = []
                for i in range(arity):
                    args.append(row.pop(0))
                value = scripts.get_script(name)(*args)
                checks.assert_has_sql_type(node_type, value)
                values.append(value)
            return _unlist(values)
        # Else, we have no join and no col referenced: just a json node (ex: name.given)
        else:
            d = dict()
            for child in children:
                name, node_type, is_list = parse_name_type(child)
                d[name] = dfs_create_fhir(project, tree[child], row, node_type)
                # Put in a list if required by typing and not already a list
                if is_list:
                    d[name] = _list(d[name])
            return d
    elif isinstance(tree, list):
        # If the element to pop(0) is a list, as we're expected a list, we make the guess
        # that both list match and we iterate over this data list to fill the fhir list
        # Note that we have no proof that they match exactly: this could fail.
        if len(row) > 0 and isinstance(row[0], list):
            join_rows = row.pop(0)
            response = []
            for join_row in join_rows:
                response.append(_unlist([dfs_create_fhir(project, t, join_row, node_type) for t in tree]))
            return response
        else:
            return [dfs_create_fhir(project, t, row, node_type) for t in tree]
    else:
        return tree


def clean_fhir(tree):
    """
    Remove all empty leaves of the fhir object (None, empty list, or nested empty things)
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
    with open(filename, 'w+') as f:
        for row in rows:
            f.write('{}\n'.format(json.dumps(row)))
