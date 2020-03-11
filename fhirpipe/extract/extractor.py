from typing import List

import pandas as pd
import logging

from sqlalchemy import create_engine, MetaData, Table, Column as AlchemyColumn
from sqlalchemy.orm import sessionmaker, Query

import fhirpipe
from fhirpipe.analyze.sql_column import SqlColumn
from fhirpipe.analyze.sql_join import SqlJoin


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
DB_DRIVERS = {"POSTGRES": "postgresql", "ORACLE": "oracle+cx_oracle"}


class Extractor:
    def __init__(self, credentials, chunksize=None):
        if credentials is None:
            credentials = fhirpipe.global_config["source"]
        db_string = self.build_db_url(credentials)

        self.engine = create_engine(db_string)
        self.metadata = MetaData(bind=self.engine)
        self.session = sessionmaker(self.engine)()

        self.chunksize = chunksize

    @staticmethod
    def build_db_url(credentials):
        login = credentials["login"]
        password = credentials["password"]
        host = credentials["host"]
        port = credentials["port"]
        database = credentials["database"]

        try:
            db_handler = DB_DRIVERS[credentials["model"]]
        except KeyError:
            raise ValueError(
                "credentials specifies the wrong database model. "
                "Only 'POSTGRES' and 'ORACLE' are currently supported."
            )

        return f"{db_handler}://{login}:{password}@{host}:{port}/{database}"

    def extract(self, resource_mapping, analysis, pk_values=None):
        """ Main method of the Extractor class.
        It builds the sql alchemy query that will fetch the columns needed from the
        source DB, run it and return the result as a pandas dataframe.

        Args:
            resource_mapping: the mapping.
            analysis: an Analyis instance built by the Analyzer.
            pk_values: it not None, the Extractor will fetch only the rows for which
                the primary key values are in pk_values.

        Returns:
            a pandas dataframe where there all the columns asked for in the mapping
        """
        logging.info(f"Extracting resource: {resource_mapping['definitionId']}")

        # Build sqlalchemy query
        query = self.sqlalchemy_query(
            analysis.columns,
            analysis.joins,
            analysis.primary_key_column,
            resource_mapping,
            pk_values,
        )

        return self.run_sql_query(query)

    def sqlalchemy_query(
        self,
        columns: List[SqlColumn],
        joins: List[SqlJoin],
        pk_column: SqlColumn,
        resource_mapping,
        pk_values,
    ) -> Query:
        """ Builds an sql alchemy query which will be run in run_sql_query.
        """
        alchemy_cols = self.get_columns(columns)
        base_query = self.session.query(*alchemy_cols)
        query_w_joins = self.apply_joins(base_query, joins)
        query_w_filters = self.apply_filters(query_w_joins, resource_mapping, pk_column, pk_values)

        return query_w_filters

    def apply_joins(self, query: Query, joins: List[SqlJoin]) -> Query:
        """ Augment the sql alchemy query with joins from the analysis.
        """
        for join in joins:
            foreign_table = self.get_table(join.right)
            query = query.join(
                foreign_table,
                self.get_column(join.right) == self.get_column(join.left),
                isouter=True,
            )
        return query

    def apply_filters(
        self, query: Query, resource_mapping, pk_column: SqlColumn, pk_values
    ) -> Query:
        """ Augment the sql alchemy query with filters from the analysis.
        """
        if pk_values is not None:
            query = query.filter(self.get_column(pk_column).in_(pk_values))

        if resource_mapping["filters"]:
            for filter in resource_mapping["filters"]:
                col = self.get_column(
                    SqlColumn(
                        filter["sqlColumn"]["table"],
                        filter["sqlColumn"]["column"],
                        filter["sqlColumn"]["owner"],
                    )
                )
                rel_method = SQL_RELATIONS_TO_METHOD[filter["relation"]]
                query = query.filter(getattr(col, rel_method)(filter["value"]))

        return query

    def run_sql_query(self, query, chunksize: int = None):
        """
        Run a sql query after opening a sql connection

        args:
            query (str): a sql query to run
            connection_type (str): the connection type / database to use
            chunksize: If specified, return an iterator where chunksize
                is the number of rows to include in each chunk.

        return:
            the result of the sql query run on the specified connection type
                or an iterator if chunksize is specified
        """
        query = query.with_labels().statement
        logging.info(f"sql query: {query}")

        pd_query = pd.read_sql_query(query, con=self.engine, chunksize=chunksize)

        # If chunksize is None, we return the dataframe for the whole DB
        # Note that we still use yield to use the for ... in ... syntax in any case
        if chunksize is None:
            yield pd.DataFrame(pd_query)
        # Otherwise, we return an iterator
        else:
            for chunk_query in pd_query:
                yield pd.DataFrame(chunk_query)

    def get_columns(self, columns: List[SqlColumn]) -> List[AlchemyColumn]:
        """ Get the sql alchemy columns corresponding to the SqlColumns (custom type)
        from the analysis.
        """
        return [self.get_column(col) for col in columns]

    def get_column(self, column: SqlColumn) -> AlchemyColumn:
        """ Get the sql alchemy column corresponding to the SqlColumn (custom type)
        from the analysis.
        """
        table = self.get_table(column)
        return table.c[column.column]

    def get_table(self, column: SqlColumn) -> Table:
        """ Get the sql alchemy table corresponding to the SqlColumn (custom type)
        from the analysis.
        """
        return Table(
            column.table, self.metadata, schema=column.owner, keep_existing=True, autoload=True
        )
