from .sql_column import SqlColumn


class SqlJoin:
    def __init__(self, column1: "SqlColumn", column2: "SqlColumn"):
        self.column1 = column1
        self.column2 = column2

    def __eq__(self, other) -> bool:
        return self.column1 == other.column1 and self.column2 == other.column2

    def __str__(self) -> str:
        return f"({self.column2}, {self.column2})"

    def __hash__(self):
        return hash(str(self))
