from typing import List
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript
from fhirpipe.analyze.sql_column import SqlColumn


class Analysis:
    def __init__(self):
        self.primary_key_column: SqlColumn = None
        self.cols = None
        self.joins = None
        self.cleaning_scripts: List[CleaningScript] = None
        self.merging_scripts: List[MergingScript] = None
        self.concept_maps: List[ConceptMap] = None
        self.squash_rules = None
