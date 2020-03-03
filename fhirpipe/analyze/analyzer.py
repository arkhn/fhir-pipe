from .mapping import (
    get_primary_key,
    find_cols_joins_maps_scripts,
    build_squash_rules,
)
from .analysis import Analysis
from .concept_map import get_concept_maps
from .cleaning_script import get_cleaning_scripts
from .merging_script import get_merging_scripts


class Analyzer:
    def analyze(self, resource_mapping):
        analysis = Analysis()

        # Get primary key table
        analysis.primary_key_table, analysis.primary_key_column = get_primary_key(resource_mapping)

        # Get concept map used in mapping
        analysis.concept_maps = get_concept_maps(resource_mapping)

        # Get cleaning scripts used in mapping
        analysis.cleaning_scripts = get_cleaning_scripts(resource_mapping)

        # Get merging scripts used in mapping
        analysis.merging_scripts = get_merging_scripts(resource_mapping)

        # Extract cols and joins
        (analysis.cols, analysis.joins,) = find_cols_joins_maps_scripts(
            resource_mapping,
            analysis.concept_maps,
            analysis.cleaning_scripts,
            analysis.merging_scripts,
        )
        # Add primary key column if it was not there
        analysis.cols.add(analysis.primary_key_column)

        # Build squash rules
        analysis.squash_rules = build_squash_rules(
            analysis.cols, analysis.joins, analysis.primary_key_table
        )

        return analysis
