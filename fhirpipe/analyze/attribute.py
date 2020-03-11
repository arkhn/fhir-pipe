from typing import List
from .sql_column import SqlColumn
from .merging_script import MergingScript


class Attribute:
    def __init__(
        self,
        path,
        columns: List[SqlColumn] = [],
        static_inputs: List[str] = [],
        merging_script: MergingScript = None,
    ):
        self.path = path
        self.columns = columns
        self.static_inputs = static_inputs
        self.merging_script = merging_script

    def add_column(self, col):
        self.columns.append(col)

    def add_static_input(self, value):
        self.static_inputs.append(value)
