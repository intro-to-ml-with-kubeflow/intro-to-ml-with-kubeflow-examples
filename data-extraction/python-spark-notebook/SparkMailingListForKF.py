#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Yes we need both these imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import *
from pyspark.sql.types import StructField, StructType
from pyspark.sql.catalog import UserDefinedFunction
import os


# In[ ]:





# In[2]:


fs_prefix = "s3a://mailinglists/" # Create with mc as in ch1


# In[3]:


os.environ["PYSPARK_PYTHON"] = "python3.6"
# See https://medium.com/@szinck/setting-up-pyspark-jupyter-and-minio-on-kubeflow-kubernetes-aab98874794f
session = (SparkSession.builder
           .appName("fetchMailingListData")
           .config("spark.executor.instances", "8")
           .config("spark.driver.memoryOverhead", "0.25")
           .config("spark.executor.memory", "6g")
           .config("spark.dynamicAllocation.enabled", "false")
           .config("spark.ui.enabled", "true")
           .config("spark.kubernetes.container.image",
                   "gcr.io/boos-demo-projects-are-rad/kubeflow/spark-worker/spark-py-36:v3.0.0-preview2-22")
           .config("spark.driver.bindAddress", "0.0.0.0")
           .config("spark.kubernetes.namespace", "kubeflow-programmerboo")
           .config("spark.master", "k8s://https://kubernetes.default")
           .config("spark.driver.host", "spark-driver.kubeflow-programmerboo.svc.cluster.local")
           .config("spark.kubernetes.executor.annotation.sidecar.istio.io/inject", "false")
           .config("spark.driver.port", "39235")
           .config("spark.blockManager.port", "39236")
            # If using minio - see https://github.com/minio/cookbook/blob/master/docs/apache-spark-with-minio.md
           .config("spark.hadoop.fs.s3a.endpoint", "minio-service.kubeflow.svc.cluster.local:9000")
           .config("fs.s3a.connection.ssl.enabled", "false")
           .config("fs.s3a.path.style.access", "true")
           # You can also add an account using the minio command as described in chapter 1
           .config("spark.hadoop.fs.s3a.access.key", "minio")
           .config("spark.hadoop.fs.s3a.secret.key", "minio123")
          ).getOrCreate()
sc = session.sparkContext


# In[4]:


# Data fetch pipeline: Download mailing list data


# In[5]:


list_name="spark-user"


# In[6]:


mailing_list_template="http://mail-archives.apache.org/mod_mbox/{list_name}/{date}.mbox"


# In[7]:


# Generate the possible dates


# In[8]:


start_year=2020 # Change to 2002 once you've verified
end_year=2021
dates = ["{:d}{:02d}".format(year, month) for year in range(start_year, end_year) for month in range (1,12)]


# In[9]:


def download_emails(date):
    import subprocess
    from mailbox import mbox
    import os
    mbox_filename = "{date}.mbox".format(date=date)
    url=mailing_list_template.format(list_name=list_name,date=date)
    subprocess.call(["wget", url])
    # Skip years that don't exist
    if not os.path.exists(mbox_filename):
        return []
    mail = mbox(mbox_filename.format(date=date), create=False)
    # LC the keys since the casing is non-consistent
    emails = list(map(lambda message: dict((k.lower(), v) for k, v in message.items()),
                                          mail.itervalues()))
    os.remove(mbox_filename)
    return emails


# In[10]:


# Optional: test that it works locally
# download_emails("202001")


# In[11]:


emails_rdd = sc.parallelize(dates).flatMap(download_emails).cache()


# In[12]:


emails_rdd.count()


# In[13]:


mailing_list_posts_mbox_df = emails_rdd.toDF(sampleRatio=1.0)


# 

# In[14]:


mailing_list_posts_mbox_df.cache()


# In[15]:


mailing_list_posts_mbox_df.select("list-id", "In-Reply-To").take(5)


# In[16]:


spark_mailing_list_data = mailing_list_posts_mbox_df.filter(
    mailing_list_posts_mbox_df["list-id"] == "<user.spark.incubator.apache.org>").repartition(60).cache()


# In[17]:


spark_mailing_list_data.show()


# In[18]:


spark_mailing_list_data.printSchema()


# In[19]:


def extract_date_from_email_datefield(datefield):
    if datefield is None:
        return None
    from datetime import datetime
    import time
    import email.utils
    parsed_date = email.utils.parsedate(datefield)
    return datetime.fromtimestamp(time.mktime((parsed_date)))


extract_date_from_email_datefield_udf = UserDefinedFunction(
    extract_date_from_email_datefield, StringType(), "extract_date_from_email_datefield")

session.catalog._jsparkSession.udf().registerPython(
    "extract_date_from_email_datefield",
    extract_date_from_email_datefield_udf._judf)


# In[20]:


# Manually verify that our date parser is looking ok
spark_mailing_list_data.select(spark_mailing_list_data["Date"],
                               extract_date_from_email_datefield_udf(spark_mailing_list_data["Date"]).alias("email_date"),
                               to_date(spark_mailing_list_data["Date"])).take(5)


# In[21]:


mailing_list_posts_in_reply_to = spark_mailing_list_data.filter(
    spark_mailing_list_data["In-Reply-To"].isNotNull()).alias("mailing_list_posts_in_reply_to")
initial_posts = spark_mailing_list_data.filter(
    spark_mailing_list_data["In-Reply-To"].isNull()).alias("initial_posts").cache()


# In[22]:


# See how many start-of-thread posts we have
initial_posts.count()


# In[23]:


mailing_list_posts_in_reply_to.select("In-Reply-To").take(10)


# In[24]:


# Ok now it's time to save these
initial_posts.write.format("parquet").save(fs_prefix + "/initial_posts")
mailing_list_posts_in_reply_to.write.format("parquet").save(fs_prefix + "/initial_posts")


# In[ ]:


# Find the initial posts where no one replied
posts_without_replies = (initial_posts.join(
        mailing_list_posts_in_reply_to,
        col("mailing_list_posts_in_reply_to.In-Reply-To") == col("initial_posts.Message-Id"),
        "left_outer")
       .filter(col("mailing_list_posts_in_reply_to.Message-Id").isNull())).cache()
posts_without_replies.count()


# In[ ]:





# In[ ]:


posts_by_date_count = spark_mailing_list_data.select(
    date_trunc("dd", from_unixtime(spark_mailing_list_data.timestamp)).alias("date")) \
    .groupBy("date").count()


# In[ ]:


posts_by_date_count.toPandas()


# In[ ]:


tokenizer = None
# TODO - fix spacy tokenizetransformer
#try:
#    tokenizer = SpacyTokenizeTransformer(inputCol="body", outputCol="body_tokens")
#except:
#tokenizer = Tokenizer(inputCol="body", outputCol="body_tokens")
spacy_tokenizer = SpacyTokenizeTransformer(inputCol="body", outputCol="body_tokens")
builtin_tokenizer = tokenizer = Tokenizer(inputCol="body", outputCol="body_tokens")
tokenizer = spacy_tokenizer


# In[ ]:


# Todo - UDF to exctract & UDF to detect programming language & UDF to extract files in a stack trace


# In[ ]:





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





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


extract_links_udf = UserDefinedFunction(
    extract_links, ArrayType(StringType()), "extract_links")

session.catalog._jsparkSession.udf().registerPython(
    "extract_links",
    extract_links_udf._judf)


extract_domains_udf = UserDefinedFunction(
    extract_domains, ArrayType(StringType()), "extract_domains")

session.catalog._jsparkSession.udf().registerPython(
    "extract_domains",
    extract_domains_udf._judf)


contains_python_stack_trace_udf = UserDefinedFunction(
    contains_python_stack_trace, BooleanType(), "contains_python_stack_trace")

session.catalog._jsparkSession.udf().registerPython(
    "contains_python_stack_trace",
    contains_python_stack_trace_udf._judf)


contains_probably_java_stack_trace_udf = UserDefinedFunction(
    contains_probably_java_stack_trace, BooleanType(), "contains_probably_java_stack_trace")

session.catalog._jsparkSession.udf().registerPython(
    "contains_probably_java_stack_trace",
    contains_probably_java_stack_trace_udf._judf)


contains_exception_in_task_udf = UserDefinedFunction(
    contains_exception_in_task, BooleanType(), "contains_exception_in_task")

session.catalog._jsparkSession.udf().registerPython(
    "contains_exception_in_task",
    contains_exception_in_task_udf._judf)


# We could make this a transformer stage, but I'm lazy so we'll just use a UDF directly.

# In[ ]:


annotated_spark_mailing_list_data = spark_mailing_list_data.select(
    "*",
    extract_links_udf(spark_mailing_list_data.body).alias("links_in_email"),
    contains_python_stack_trace_udf(spark_mailing_list_data.body).alias("contains_python_stack_trace").cast("double"),
    contains_probably_java_stack_trace_udf(spark_mailing_list_data.body).alias("contains_java_stack_trace").cast("double"),
    contains_exception_in_task_udf(spark_mailing_list_data.body).alias("contains_exception_in_task").cast("double"))


# In[ ]:


annotated_spark_mailing_list_data.cache()


# In[ ]:


annotated_spark_mailing_list_data.show()


# In[ ]:


further_annotated = annotated_spark_mailing_list_data.withColumn(
    "domain_links",
    extract_domains_udf(annotated_spark_mailing_list_data.links_in_email)).withColumn(
    "is_thread_start",
    isnull(annotated_spark_mailing_list_data.in_reply_to).cast(DoubleType()))
# Long story, allow mixed UDF types
further_annotated.cache()
further_annotated.count()


# In[ ]:





# In[ ]:


body_hashing = HashingTF(inputCol="body_tokens", outputCol="raw_body_features", numFeatures=10000)
body_idf =IDF(inputCol="raw_body_features", outputCol="body_features")


# In[ ]:


body_word2Vec = Word2Vec(vectorSize=5, minCount=0, numPartitions=10, inputCol="body_tokens", outputCol="body_features")


# In[ ]:





# In[ ]:


assembler = VectorAssembler(
    inputCols=["body_features", "contains_python_stack_trace", "contains_java_stack_trace", 
              "contains_exception_in_task", "is_thread_start", "domain_features"],
    outputCol="features")


# In[ ]:


kmeans = KMeans(featuresCol="features", k=2, seed=42)


# In[ ]:


featureprep_pipeline = Pipeline(stages=[tokenizer, body_hashing, body_idf, domains_hashing, domains_idf, assembler])
pipeline = Pipeline(stages=[featureprep_pipeline, kmeans])


# In[ ]:





# In[ ]:


from pyspark.ml.pipeline import Transformer
isinstance(tokenizer, Transformer)


# In[ ]:


test = further_annotated.limit(10).cache()
test.count()


# In[ ]:


test_model = pipeline.fit(test)


# In[ ]:


test_result = test_model.transform(test)
test_result.toPandas()


# In[ ]:


data_prep_transformer = dataprep_pipeline.fit(further_annotated)
preped_data = data_prep_model.transform(further_annotated)
preped_data.count()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# 

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




