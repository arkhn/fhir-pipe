from typing import Dict
from fhirpipe.analyze.concept_map import ConceptMap
from fhirpipe.analyze.cleaning_script import CleaningScript
from fhirpipe.analyze.merging_script import MergingScript


class Analysis:
    def __init__(self):
        self.primary_key_table = None
        self.primary_key_column = None
        self.cols = None
        self.joins = None
        self.cleaning_scripts: Dict[str, CleaningScript] = None
        self.merging_scripts: Dict[str, MergingScript] = None
        self.squash_rules = None
        self.concept_maps: Dict[str, ConceptMap] = None
