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
    Node in the graph of dependency. Represents a table, and attribute
    connections link to other nodes / tables.
    """

    def __init__(self, table_name):
        self.name = table_name
        self.connections = []

    def __repr__(self):
        string = "[{} O2O:({}) O2M:({})]".format(
            self.name,
            ",".join([j.name for j in self.one_to_one]),
            ",".join([j.name for j in self.connections]),
        )
        return string

    def connect(self, table):
        """
        Declare a join
        :param table: end table of the join
        """
        if table not in self.connections:
            self.connections.append(table)

    def connected(self, table):
        return table in (self.one_to_one + self.connections)
