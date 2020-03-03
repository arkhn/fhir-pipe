from typing import Dict
from fhirpipe.analyze.concept_map import ConceptMap


class Analysis:
    def __init__(self):
        self.primary_key_table = None
        self.primary_key_column = None
        self.cols = None
        self.joins = None
        self.cleaning = None
        self.merging = None
        self.squash_rules = None
        self.concept_maps: Dict[str, ConceptMap] = None
