from typing import List, Set

from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin
from fhirpipe.analyze.attribute import Attribute


class Analysis:
    def __init__(self):
        self.attributes: List[Attribute] = []
        self.columns: Set[SqlColumn] = set()
        self.joins: Set[SqlJoin] = set()
        self.primary_key_column: SqlColumn = None
        self.squash_rules = None
        self.reference_paths: List[str] = []

    def reset(self):
        self.attributes = []
        self.columns = set()
        self.joins = set()
        self.primary_key_column = None
        self.squash_rules = None
        self.reference_paths = []

    def add_column(self, column):
        self.columns.add(column)

    def add_join(self, join):
        self.joins.add(join)
