import json


class Log:
    """
    The write Store class is used to write to disc some values and get them
    back in a different execution.
    It is used when the system crashes for example.
    """

    def __init__(self, log_filename="store.tmp"):
        self.log_filename = "store.tmp"
        self.data = None

    def get(self, name, default):
        """
        Returns values from the write store
        :param name: id of the variable to retrieve
        :param default: default value if unset
        :return: the variable value stored or default
        """
        if log.data is None:
            try:
                with open(self.log_filename) as log_file:
                    log.data = json.loads(log_file.read())
            except FileNotFoundError:
                with open(self.log_filename, "w") as log_file:
                    log_file.write("{}")
                self.get(name, default)

        if name in log.data:
            return log.data[name]
        else:
            return default

    def set(self, name, value):
        """
        Write one value in the write store
        :param name: id of the variable to retrieve
        :param value: the value of the variable
        """
        log.data[name] = value
        with open(self.log_filename, "w") as log_file:
            log_file.write(json.dumps(log.data))

    def rm(self, name):
        """
        Remove a variable in the write store
        :param name: id of the variable to delete
        """
        del log.data[name]
        with open(self.log_filename, "w") as log_file:
            log_file.write(json.dumps(log.data))


log = Log()
