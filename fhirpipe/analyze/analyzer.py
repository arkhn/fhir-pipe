from .mapping import (
    get_primary_key,
    analyze_mapping,
    build_squash_rules,
)
from .analysis import Analysis


class Analyzer:
    def analyze(self, resource_mapping):
        analysis = Analysis()

        # Get primary key table
        analysis.primary_key_column = get_primary_key(
            resource_mapping
        )

        analysis.attributes, analysis.columns, analysis.joins = analyze_mapping(resource_mapping)

        # Add primary key to columns to fetch if needed
        analysis.columns.add(analysis.primary_key_column)

        # Build squash rules
        analysis.squash_rules = build_squash_rules(
            analysis.columns, analysis.joins, analysis.primary_key_column.table_name()
        )

        return analysis
