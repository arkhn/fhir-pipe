from .mapping import (
    get_primary_key,
    find_cols_joins_maps_scripts,
    build_squash_rules,
)
from .analysis import Analysis


class Analyzer:
    def analyze(self, resource_mapping):
        analysis = Analysis()

        # Get primary key table
        analysis.primary_key_table, analysis.primary_key_column = get_primary_key(
            resource_mapping
        )

        # Extract cols, joins, concept_maps, cleaning_scripts, and merging_scripts
        (
            analysis.cols,
            analysis.joins,
            analysis.concept_maps,
            analysis.cleaning_scripts,
            analysis.merging_scripts,
        ) = find_cols_joins_maps_scripts(resource_mapping)

        # Add primary key column if it was not there
        analysis.cols.add(analysis.primary_key_column)

        # Build squash rules
        analysis.squash_rules = build_squash_rules(
            analysis.cols, analysis.joins, analysis.primary_key_table
        )

        return analysis
