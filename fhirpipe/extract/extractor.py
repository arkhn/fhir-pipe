import logging

from fhirpipe.extract.sql import (
    build_sql_filters,
    build_sql_query,
    run_sql_query,
)


class Extractor:
    def __init__(self, connection, chunksize=None):
        self.connection = connection
        self.chunksize = chunksize

    def extract(self, resource_mapping, analysis, primary_key_values=None):
        logging.info("Extracting resource: %s", resource_mapping["definitionId"])

        # Build sql filters (for now, it's only for row selection)
        sql_filters = build_sql_filters(
            resource_mapping, analysis.primary_key_column, primary_key_values
        )

        # Build the sql query
        sql_query = build_sql_query(
            analysis.cols, analysis.joins, analysis.primary_key_table, sql_filters
        )
        logging.info("sql query: %s", sql_query)

        # Run the sql query
        logging.info("Launching query...")
        return run_sql_query(self.connection, sql_query, chunksize=self.chunksize)
