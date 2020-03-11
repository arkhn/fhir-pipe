from typing import List

from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin
from fhirpipe.analyze.attribute import Attribute


class Analysis:
    def __init__(self):
        self.attributes: List[Attribute] = None
        self.columns: List[SqlColumn] = None
        self.joins: List[SqlJoin] = None
        self.primary_key_column: SqlColumn = None
        self.squash_rules = None
