from sqlalchemy import create_engine

import logging

import fhirpipe
from fhirpipe.extract.sql import (
    build_db_string,
    build_sql_filters,
    build_sql_query,
    run_sql_query,
)


class Extractor:
    def __init__(self, credentials, chunksize=None):
        if credentials is None:
            credentials = fhirpipe.global_config["default-source-creds"]
        db_string = build_db_string(credentials)

        self.engine = create_engine(db_string)
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
        return run_sql_query(self.engine, sql_query, chunksize=self.chunksize)
