from fhirpipe.console import WELCOME_MSG
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, col, count, desc

import fhirpipe

spark = SparkSession \
        .builder \
        .appName("Bundle FHIR resources to hive tables") \
        .enableHiveSupport() \
        .getOrCreate()

df = fhirpipe.load.spark_sql.load_table(spark, "MIMICIII.PATIENTS")
