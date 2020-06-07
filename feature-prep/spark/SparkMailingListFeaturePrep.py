#!/usr/bin/env python
# coding: utf-8

# In[ ]:

# Yes we need both these imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, lit, isnull
from pyspark.sql.types import *
from pyspark.sql.types import StructField, StructType
from pyspark.sql.catalog import UserDefinedFunction
from pyspark.ml.feature import *
from pyspark.ml.pipeline import Pipeline
import os

# In[ ]:

# In[ ]:

fs_prefix = "s3a://kf-book-examples/mailing-lists"  # Create with mc as in ch1

# In[ ]:

os.environ["PYSPARK_PYTHON"] = "python3.6"
# See https://medium.com/@szinck/setting-up-pyspark-jupyter-and-minio-on-kubeflow-kubernetes-aab98874794f
session = (
    SparkSession.builder.appName("processMailingListData").config(
        "spark.executor.instances",
        "8").config("spark.driver.memoryOverhead",
                    "0.25").config("spark.executor.memory", "10g").config(
                        "spark.dynamicAllocation.enabled", "false").
    config("spark.ui.enabled", "true").config(
        "spark.kubernetes.container.image",
        "gcr.io/boos-demo-projects-are-rad/kubeflow/spark-worker/spark-py-36:v3.0.0-preview2-23"
    ).config("spark.driver.bindAddress",
             "0.0.0.0").config("spark.kubernetes.namespace",
                               "kubeflow-programmerboo").
    config("spark.master", "k8s://https://kubernetes.default").config(
        "spark.driver.host",
        "spark-driver.kubeflow-programmerboo.svc.cluster.local").config(
            "spark.kubernetes.executor.annotation.sidecar.istio.io/inject",
            "false").config("spark.driver.port",
                            "39235").config("spark.blockManager.port", "39236")
    # If using minio - see https://github.com/minio/cookbook/blob/master/docs/apache-spark-with-minio.md
    .config("spark.hadoop.fs.s3a.endpoint",
            "minio-service.kubeflow.svc.cluster.local:9000").config(
                "fs.s3a.connection.ssl.enabled",
                "false").config("fs.s3a.path.style.access", "true")
    # You can also add an account using the minio command as described in chapter 1
    .config("spark.hadoop.fs.s3a.access.key",
            "minio").config("spark.hadoop.fs.s3a.secret.key",
                            "minio123")).getOrCreate()
sc = session.sparkContext

# In[ ]:

#Load data from the previous stage
#tag::load_data[]
initial_posts = session.read.format("parquet").load(fs_prefix +
                                                    "/initial_posts")
ids_in_reply = session.read.format("parquet").load(fs_prefix + "/ids_in_reply")
#end::load_data[]

# In[ ]:

# Load data from the previous stage while checking the schema
#tag::load_with_schema[]
ids_schema = StructType([
    StructField("In-Reply-To", StringType(), nullable=True),
    StructField("message-id", StringType(), nullable=True)
])
ids_in_reply = session.read.format("parquet").schema(ids_schema).load(
    fs_prefix + "/ids_in_reply")
#end::load_with_schema[]

# In[ ]:

# Cache the data
initial_posts = initial_posts.alias("initial_posts").cache()
ids_in_reply = ids_in_reply.alias("ids_in_reply").cache()

# In[ ]:

# We can write random SQL -- although we need to wait for preview 3 cause it was taken out in preview1
#tag::direct_sql[]
#ids_in_reply.registerTempTable("cheese")
#no_text = session.sql("select * from cheese where body = '' AND subject = ''")
#end::direct_sql[]

# In[ ]:

# Drop bad data
#tag::drop_bad_fields[]
initial_posts_count = initial_posts.count()
initial_posts_cleaned = initial_posts.na.drop(how='any',
                                              subset=['body', 'from'])
initial_posts_cleaned_count = initial_posts_cleaned.count()
#end::drop_bad_fields[]

# In[ ]:

initial_posts.show()

# In[ ]:

# Start with computing the labels
# Find the initial posts where no one replied
posts_with_replies = (initial_posts.join(
    ids_in_reply,
    col("ids_in_reply.In-Reply-To") == col("initial_posts.Message-Id"),
    "left_outer").filter(col("ids_in_reply.In-Reply-To").isNotNull())).cache()
posts_with_replies.count()
post_ids_with_replies = (posts_with_replies.select(
    col("initial_posts.Message-Id").alias("id")).withColumn(
        "has_reply", lit(1.0))).alias("post_with_replies")

joined_posts = initial_posts.join(
    post_ids_with_replies,
    col("initial_posts.Message-Id") == col("post_with_replies.id"))

# In[ ]:

joined_posts.show()

# In[ ]:

posts_with_labels = joined_posts.na.fill({"has_reply": 0.0}).cache()
posts_with_labels.count()

# In[ ]:


def extract_links(body):
    import re
    link_regex_str = r'(http(|s)://(.*?))([\s\n]|$)'
    itr = re.finditer(link_regex_str, body, re.MULTILINE)
    return list(map(lambda elem: elem.group(1), itr))


def extract_domains(links):
    from urllib.parse import urlparse

    def extract_domain(link):
        try:
            nloc = urlparse(link).netloc
            # We want to drop www and any extra spaces wtf nloc on the spaces.
            regex_str = r'^(www\.|)(.*?)\s*$'
            match = re.search(regex_str, nloc)
            return match.group(2)
        except:
            return None

    return list(map(extract_domain, links))


def contains_python_stack_trace(body):
    return "Traceback (most recent call last)" in body


def contains_probably_java_stack_trace(body):
    # Look for something based on regex
    # Tried https://stackoverflow.com/questions/20609134/regular-expression-optional-multiline-java-stacktrace - more msg looking
    # Tried https://stackoverflow.com/questions/3814327/regular-expression-to-parse-a-log-file-and-find-stacktraces
    # Yes the compile is per call, but it's cached so w/e
    import re
    stack_regex_str = r'^\s*(.+Exception.*):\n(.*\n){0,3}?(\s+at\s+.*\(.*\))+'
    match = re.search(stack_regex_str, body, re.MULTILINE)
    return match is not None


def contains_exception_in_task(body):
    # Look for a line along the lines of ERROR Executor: Exception in task
    return "ERROR Executor: Exception in task" in body


# In[ ]:

extract_links_udf = UserDefinedFunction(extract_links, ArrayType(StringType()),
                                        "extract_links")

session.catalog._jsparkSession.udf().registerPython("extract_links",
                                                    extract_links_udf._judf)

extract_domains_udf = UserDefinedFunction(extract_domains,
                                          ArrayType(StringType()),
                                          "extract_domains")

session.catalog._jsparkSession.udf().registerPython("extract_domains",
                                                    extract_domains_udf._judf)

contains_python_stack_trace_udf = UserDefinedFunction(
    contains_python_stack_trace, BooleanType(), "contains_python_stack_trace")

session.catalog._jsparkSession.udf().registerPython(
    "contains_python_stack_trace", contains_python_stack_trace_udf._judf)

contains_probably_java_stack_trace_udf = UserDefinedFunction(
    contains_probably_java_stack_trace, BooleanType(),
    "contains_probably_java_stack_trace")

session.catalog._jsparkSession.udf().registerPython(
    "contains_probably_java_stack_trace",
    contains_probably_java_stack_trace_udf._judf)

contains_exception_in_task_udf = UserDefinedFunction(
    contains_exception_in_task, BooleanType(), "contains_exception_in_task")

session.catalog._jsparkSession.udf().registerPython(
    "contains_exception_in_task", contains_exception_in_task_udf._judf)

# We could make this a transformer stage, but I'm lazy so we'll just use a UDF directly.

# In[ ]:

annotated_spark_mailing_list_data = posts_with_labels.select(
    "*",
    extract_links_udf(posts_with_labels["body"]).alias("links_in_email"),
    contains_python_stack_trace_udf(posts_with_labels.body).alias(
        "contains_python_stack_trace").cast("double"),
    contains_probably_java_stack_trace_udf(posts_with_labels.body).alias(
        "contains_java_stack_trace").cast("double"),
    contains_exception_in_task_udf(posts_with_labels.body).alias(
        "contains_exception_in_task").cast("double"))

# In[ ]:

annotated_spark_mailing_list_data.cache()

# In[ ]:

annotated_spark_mailing_list_data.show()

# In[ ]:

further_annotated = annotated_spark_mailing_list_data.withColumn(
    "domain_links",
    extract_domains_udf(annotated_spark_mailing_list_data.links_in_email))
# Long story, allow mixed UDF types
further_annotated.cache()
further_annotated.count()

# In[ ]:

#tag::make_features[]
tokenizer = Tokenizer(inputCol="body", outputCol="body_tokens")
body_hashing = HashingTF(inputCol="body_tokens",
                         outputCol="raw_body_features",
                         numFeatures=10000)
body_idf = IDF(inputCol="raw_body_features", outputCol="body_features")
body_word2Vec = Word2Vec(vectorSize=5,
                         minCount=0,
                         numPartitions=10,
                         inputCol="body_tokens",
                         outputCol="body_vecs")
assembler = VectorAssembler(inputCols=[
    "body_features", "body_vecs", "contains_python_stack_trace",
    "contains_java_stack_trace", "contains_exception_in_task"
],
                            outputCol="features")
#end::make_features[]

# In[ ]:

featureprep_pipeline = Pipeline(
    stages=[tokenizer, body_hashing, body_idf, body_word2Vec, assembler])

# In[ ]:

featureprep_pipeline_transformer = featureprep_pipeline.fit(further_annotated)
preped_data = featureprep_pipeline_transformer.transform(further_annotated)

# In[ ]:

featureprep_pipeline_transformer.write().save(fs_prefix + "/feature_prep-2")

# In[ ]:

preped_data.write.format("parquet").mode("overwrite").save(fs_prefix +
                                                           "/prepared_data")
