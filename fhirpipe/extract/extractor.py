import logging
from collections import defaultdict

from fhirpipe.extract.mapping import (
    prune_fhir_resource,
    get_primary_key,
    find_cols_joins_and_scripts,
    build_squash_rules,
    find_reference_attributes,
)
from fhirpipe.extract.sql import (
    build_sql_filters,
    build_sql_query,
    run_sql_query,
)


class Extractor:
    def __init__(
        self, connection, chunksize
    ):
        self.connection = connection
        self.chunksize = chunksize

        # To be used by transformer
        self.fhirType = None
        self.df = None
        self.squash_rules = None
        self.cols = None
        self.cleaning = None
        self.merging = None
        self.primary_key_column = None
        self.reference_attributes = defaultdict(set)

    def extract(self, resource_structure):
        self.fhirType = resource_structure["fhirType"]
        logging.info("Extracting resource: %s", self.fhirType)

        resource_structure = prune_fhir_resource(resource_structure)

        # Get primary key table
        primary_key_table, self.primary_key_column = get_primary_key(resource_structure)

        # Extract cols and joins
        self.cols, joins, self.cleaning, self.merging = find_cols_joins_and_scripts(
            resource_structure
        )

        # Build sql filters (for now, it's only for row selection)
        sql_filters = build_sql_filters(self.primary_key_column, self.primary_key_values)

        # Build the sql query
        sql_query = build_sql_query(self.cols, joins, primary_key_table, sql_filters)
        logging.info("sql query: %s", sql_query)

        # Build squash rules
        self.squash_rules = build_squash_rules(self.cols, joins, primary_key_table)

        # Get all the attributes that are references for future binding
        for attr in find_reference_attributes(resource_structure):
            self.reference_attributes[self.fhirType].add(attr)

        # Run the sql query
        logging.info("Launching query...")
        self.df = run_sql_query(self.connection, sql_query, chunksize=self.chunksize)
