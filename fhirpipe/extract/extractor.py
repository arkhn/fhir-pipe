from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

import logging

import fhirpipe
from fhirpipe.extract.sql import build_db_url, run_sql_query
from fhirpipe.analyze.sql_column import SqlColumn


SQL_RELATIONS_TO_METHOD = {
    "<": "__lt__",
    "<=": "__le__",
    "<>": "__ne__",
    "=": "__eq__",
    ">": "__gt__",
    ">=": "__ge__",
    # not handled yet
    # "BETWEEN": "",
    "IN": "in_",
    "LIKE": "like",
}


class Extractor:
    def __init__(self, credentials, chunksize=None):
        if credentials is None:
            credentials = fhirpipe.global_config["source"]
        db_string = build_db_url(credentials)

        self.engine = create_engine(db_string)
        self.metadata = MetaData(bind=self.engine)
        self.session = sessionmaker(self.engine)()

        self.chunksize = chunksize

    def extract(self, resource_mapping, analysis, pk_values=None):
        logging.info(f"Extracting resource: {resource_mapping['definitionId']}")

        # Build sqlalchemy query
        query = self.sqlalchemy_query(
            analysis.cols,
            analysis.joins,
            analysis.primary_key_table,
            analysis.primary_key_column,
            resource_mapping,
            pk_values,
        )
        logging.info(f"sql query: {query}")

        return run_sql_query(self.engine, query)

    def sqlalchemy_query(self, columns, joins, table_name, pk_column, resource_mapping, pk_values):
        alchemy_cols = self.get_columns(columns)
        base_query = self.session.query(*alchemy_cols)
        query_w_joins = self.apply_joins(base_query, joins)
        query_w_filters = self.apply_filters(query_w_joins, resource_mapping, pk_column, pk_values)

        return query_w_filters.statement

    def apply_joins(self, query, joins):
        for join in joins:
            foreign_table = self.get_table(join.column2.table, join.column2.owner)
            query = query.join(
                foreign_table,
                self.get_column(join.column2) == self.get_column(join.column1),
                isouter=True,
            )
        return query

    def apply_filters(self, query, resource_mapping, pk_column, pk_values):
        if resource_mapping["filters"]:
            for filter in resource_mapping["filters"]:
                col_name = filter["sqlColumn"]
                col = self.get_column(
                    SqlColumn(col_name["table"], col_name["column"], col_name["owner"])
                )
                rel_method = SQL_RELATIONS_TO_METHOD[filter['relation']]
                query = query.filter(col.__getattr__(rel_method)(filter['value']))

        if pk_values is not None:
            query = query.filter(self.get_column(pk_column).in_(pk_values))

        return query

    def get_columns(self, columns):
        return [self.get_column(col) for col in columns]

    def get_column(self, column):
        table = self.get_table(column.table, column.owner)
        return table.c.__getattr__(column.column)

    def get_table(self, table, owner):
        return Table(table, self.metadata, schema=owner, keep_existing=True, autoload=True)
