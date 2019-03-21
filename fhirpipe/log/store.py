import json


class Store:
    """
    The log Store class is used to write to disc some values and get them
    back in a different execution.
    It is used when the system crashes for example.
    """

    def __init__(self):
        self.data = None


store = Store()

log_filename = "store.tmp"


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
            with open(log_filename, "w") as log_file:
                log_file.write("{}")
            get(name, default)

    if name in store.data:
        return store.data[name]
    else:
        return default


def set(name, value):
    """
    Write one value in the log store
    :param name: id of the variable to retrieve
    :param value: the value of the variable
    """
    store.data[name] = value
    with open(log_filename, "w") as log_file:
        log_file.write(json.dumps(store.data))


def rm(name):
    """
    Remove a variable in the log store
    :param name: id of the variable to delete
    """
    del store.data[name]
    with open(log_filename, "w") as log_file:
        log_file.write(json.dumps(store.data))
