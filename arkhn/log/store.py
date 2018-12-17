import json


class Store:
    def __init__(self):
        self.data = None

store = Store()

log_filename = 'store.tmp'


def get(name, default):
    """
    Returns values from the log store
    :param name: id of the variable to retrieve
    :param default: default value if unset
    :return: the variable value stored or default
    """
    if store.data is None:
        try:
            with open(log_filename) as log_file:
                store.data = json.loads(log_file.read())
        except FileNotFoundError:
            with open(log_filename, 'w') as log_file:
                log_file.write('{}')
            get(name, default)

    if name in store.data:
        return store.data[name]
    else:
        return default


def set(name, value):
    store.data[name] = value
    with open(log_filename, 'w') as log_file:
        log_file.write(json.dumps(store.data))


def rm(name):
    del store.data[name]
    with open(log_filename, 'w') as log_file:
        log_file.write(json.dumps(store.data))
