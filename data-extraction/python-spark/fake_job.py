# Yes we need both these imports
#tag::imports[]
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import *
#end::imports[]
from pyspark.sql.catalog import UserDefinedFunction
import os

#tag::basic_session[]
session = SparkSession.builder.getOrCreate()
#end::basic_session[]
