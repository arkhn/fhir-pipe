import json
import yaml
import re
import logging
from os import listdir
from os.path import isfile, join

from arkhn import scripts
from arkhn.parser import checks

path = "DataTypes/"


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
    r = re.compile(r'^([^\<]*)(?:\<(.*)\>)?')
    name, node_type = r.findall(name_type)[0]

    is_list = node_type.startswith('list')
    if len(node_type.split('::')) > 1:
        node_type = node_type.split('::')[1]
    elif is_list:
        node_type = None
    return name, node_type, is_list


def is_node_type_templatable(type_name):
    """
    Check that the node_type is compatible with templating
    """
    datatypes = [
        filename.split('.')[0]
        for filename in listdir(path)
        if isfile(join(path, filename))
    ]
    return type_name in datatypes


def build_sql_query(resource, info):
    """
    Take a Resource (eg Patient) scheme in input
    Output a sql query to fill this resource
    """
    table_name = get_table_name(info['source_table'] + '.*')

    # Get the info about the columns and joins to query
    d = dfs_find_sql_cols_joins(resource, source_table=table_name)
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
    squash_rules = []
    print(squash_rules_tables)
    for rule in squash_rules_tables:
        one_table, many_table = rule
        one_cols, many_cols = [], []
        for i, col in enumerate(col_names):
            table = get_table_name(col)
            if table == one_table:
                one_cols.append(i)
            elif table == many_table:
                many_cols.append(i)
        squash_rules.append((one_cols, many_cols))

    join_graph = []
    print(squash_rules_tables)
    for rule in squash_rules_tables:
        one_table, many_table = rule
        one_cols, many_cols = [], []
        for i, col in enumerate(col_names):
            table = get_table_name(col)
            if table == one_table:
                one_cols.append(i)
            elif table == many_table:
                many_cols.append(i)
        squash_rules.append((one_cols, many_cols))
    return sql_query, squash_rules


class Table():
    def __init__(self):
        self.one_to_one = []
        self.one_to_many = []

    def connect(self, table, join_type):
        if join_type == 'OneToOne':
            self.one_to_one.append(table)
        elif join_type == 'OneToMany':
            self.one_to_many.append(table)
        else:
            raise TypeError('Join type is not valid:', join_type)

    def connected(self, table):
        return table in (self.one_to_one + self.one_to_many)


class DependencyGraph():
    def __init__(self):
        self.nodes = {}

    def has(self, table):
        return table in self.nodes

    def add(self, table):
        node = Table(table)
        self.nodes[table] = node

    def get(self, table):
        if not self.has(self, table):
            self.add(self, table)
        return self.nodes[table]


def parse_joins(joins):
    """
    Transform a join info into SQL fragments.
    For OneToMany joins, list the joins: for example if you
    join people with bank accounts on guy.id = account.owner_id, you want at the end to
    have for a single guy to have a single instance with an attribute accounts. So you
    need to remember to group all accounts for a single guy.
    Input:
        (<type_of_join>, "<owner>.<table>.<col>=<owner>.<join_table>.<join_col>")
    Return:
        (
            "<join_table>",
            "<table>.<col> = <join_table>.<join_col>"
        ),
        ((table_guy, table_accounts), etc)
    """
    print(joins)
    joins_elems = dict()
    joins_to_many = []
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


def load_template(data_type, template_id):
    """
    Return the dict template of a resource with id template_id
    """
    with open(path + data_type + '.yml', 'r') as stream:
        try:
            data = yaml.load(stream)
            template = data[data_type][template_id]
            return template
        except yaml.YAMLError as exc:
            print(exc)
    return None


def dfs_find_sql_cols_joins(tree, node_type=None, source_table=None):
    """
        Run through the dict/tree of a Resource (and the references to templates)
        To find:
        - All columns name to select
        - All joins necessary to collect the data
    """
    if isinstance(tree, dict):
        return find_cols_joins_in_object(tree, node_type, source_table)
    elif isinstance(tree, list) and len(tree) > 0:
        response = {'cols': [], 'joins': []}
        for t in tree:
            d = find_cols_joins_in_object(t, node_type, source_table)
            response['cols'] += d['cols']
            response['joins'] += d['joins']
        return response
    else:
        return {'cols': [], 'joins': []}


def find_cols_joins_in_object(tree, node_type, source_table):
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
        assert is_node_type_templatable(node_type), "Can't have a template for type {}".format(node_type)
        template_ids = _list(template_ids)
        template_cols = []
        template_joins = []
        for template_id in template_ids:
            template = load_template(node_type, template_id)
            template_d = dfs_find_sql_cols_joins(template, node_type)
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
            d = dfs_find_sql_cols_joins(tree[child], node_type, source_table)
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


def dfs_create_fhir(tree, row, node_type=None):
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
            print('_template_id', tree['_template_id'])
            # Load the referenced template
            template_ids = _list(tree['_template_id'])

            response = []
            if len(row) > 0 and isinstance(row[0], list):
                join_rows = row.pop(0)
                # t_row is assumed to be [['a1', 'b1', ...],['a2', 'b2', ...]]
                for join_row in join_rows:
                    for template_id in template_ids:
                        template = load_template(node_type, template_id)
                        resp = dfs_create_fhir(template, join_row, node_type)
                        response.append(resp)
            else:
                for template_id in template_ids:
                    template = load_template(node_type, template_id)
                    resp = dfs_create_fhir(template, row, node_type)
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
                d[name] = dfs_create_fhir(tree[child], row, node_type)
                # Put in a list if required by typing and not already a list
                if is_list:
                    d[name] = _list(d[name])
            return d
    elif isinstance(tree, list):
        if len(row) > 0 and isinstance(row[0], list):
            print('LIST FOUND')
            print(row[0])
            join_rows = row.pop(0)
            response = []
            for join_row in join_rows:
                print('>> ', len(join_row))
                response.append([dfs_create_fhir(t, join_row, node_type) for t in tree])
            return response
        else:
            return [dfs_create_fhir(t, row, node_type) for t in tree]
    else:
        return tree


def clean_fhir(tree):
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
