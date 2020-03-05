from typing import List
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript


class Analysis:
    def __init__(self):
        self.primary_key_table = None
        self.primary_key_column = None
        self.cols = None
        self.joins = None
        self.cleaning_scripts: List[CleaningScript] = None
        self.merging_scripts: List[MergingScript] = None
        self.concept_maps: List[ConceptMap] = None
        self.squash_rules = None
