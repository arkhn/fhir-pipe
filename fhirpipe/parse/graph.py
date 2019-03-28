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

