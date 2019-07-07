from fhirpipe.config import Config
from pyspark.sql import SparkSession


def load_sql_table(spark, config, table):
    """
    Returns a dataframe based on a table available in the connected database from config.
    args:
        spark (SparkSession): the spark context.
        table (str): the table name written as such: `schema_name.table_name` to be turned into a Spark dataframe

    """


    sql_config = Config("spark_slq").to_dict()
    if connection_type is None:
        connection_type = sql_config["default"]
    connection = sql_config[connection_type]

    return spark.format("jdbc") \
        .option("url", "jdbc:{}:{}".format(connection["driver"], connection["database"])) \
        .option("dbtable", table) \
        .option('user', connection["user"]) \
        .option("password", connection["password"]) \
        .load()