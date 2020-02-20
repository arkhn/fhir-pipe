from fhirpipe.analyze.mapping import (
    get_primary_key,
    find_cols_joins_and_scripts,
    build_squash_rules,
)


class Analyzer:
    def analyze(self, resource_mapping):
        analysis = {}

        # Get primary key table
        analysis["primary_key_table"], analysis["primary_key_column"] = get_primary_key(
            resource_mapping
        )

        # Extract cols and joins
        (
            analysis["cols"],
            analysis["joins"],
            analysis["cleaning"],
            analysis["merging"],
        ) = find_cols_joins_and_scripts(resource_mapping)
        # Add primary key column if it was not there
        analysis["cols"].add(analysis["primary_key_column"])

        # Build squash rules
        analysis["squash_rules"] = build_squash_rules(
            analysis["cols"], analysis["joins"], analysis["primary_key_table"]
        )

        return analysis
