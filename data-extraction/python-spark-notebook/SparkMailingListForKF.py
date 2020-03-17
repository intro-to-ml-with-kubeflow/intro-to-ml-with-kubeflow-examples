#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Yes we need both these imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import *
from pyspark.sql.types import StructField, StructType
from pyspark.sql.catalog import UserDefinedFunction
import os


# In[ ]:





# In[ ]:


fs_prefix = "s3a://kf-book-examples/mailing-lists" # Create with mc as in ch1


# In[ ]:


# See https://medium.com/@szinck/setting-up-pyspark-jupyter-and-minio-on-kubeflow-kubernetes-aab98874794f
#tag::configurePythonVersion[]
os.environ["PYSPARK_PYTHON"] = "python3.6"
#end::configurePythonVersion[]
session = (SparkSession.builder
           .appName("fetchMailingListData")
           .config("spark.executor.instances", "8")
           .config("spark.driver.memoryOverhead", "0.25")
           .config("spark.executor.memory", "6g")
           .config("spark.dynamicAllocation.enabled", "false")
           .config("spark.ui.enabled", "true")
           .config("spark.kubernetes.container.image",
                   "gcr.io/boos-demo-projects-are-rad/kubeflow/spark-worker/spark-py-36:v3.0.0-preview2-23")
            #tag::notebookSession[]
           .config("spark.driver.bindAddress", "0.0.0.0")
           .config("spark.kubernetes.namespace", "kubeflow-programmerboo")
           .config("spark.master", "k8s://https://kubernetes.default")
           .config("spark.driver.host", "spark-driver.kubeflow-programmerboo.svc.cluster.local")
           .config("spark.kubernetes.executor.annotation.sidecar.istio.io/inject", "false")
           .config("spark.driver.port", "39235")
           .config("spark.blockManager.port", "39236")
            #end::notebookSession[]
            # If using minio - see https://github.com/minio/cookbook/blob/master/docs/apache-spark-with-minio.md
            #tag::minio[]
           .config("spark.hadoop.fs.s3a.endpoint", "minio-service.kubeflow.svc.cluster.local:9000")
           .config("fs.s3a.connection.ssl.enabled", "false")
           .config("fs.s3a.path.style.access", "true")
           # You can also add an account using the minio command as described in chapter 1
           .config("spark.hadoop.fs.s3a.access.key", "minio")
           .config("spark.hadoop.fs.s3a.secret.key", "minio123")
            #end::minio[]
          ).getOrCreate()
sc = session.sparkContext


# In[ ]:


# Data fetch pipeline: Download mailing list data


# In[ ]:


list_name="spark-user"


# In[ ]:


mailing_list_template="http://mail-archives.apache.org/mod_mbox/{list_name}/{date}.mbox"


# In[ ]:


# Generate the possible dates


# In[ ]:


start_year=2019 # Change to 2002 once you've verified
end_year=2021
dates = ["{:d}{:02d}".format(year, month) for year in range(start_year, end_year) for month in range (1,12)]


# In[ ]:


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
    def get_body(message):
        content_type = message.get_content_type()
        # Multi-part messages
        if message.is_multipart():
            return "".join(map(get_body, message.get_payload()))
        elif "text" in content_type or "html" in content_type:
            return message.get_payload()
        else:
            return ""
    def message_to_dict(message):
        ret = dict((k.lower(), v) for k, v in message.items())
        ret["multipart"] = message.is_multipart()
        ret["body"] = get_body(message)
        return ret
    emails = list(map(message_to_dict, mail.itervalues()))
    os.remove(mbox_filename)
    return emails


# In[ ]:


# Optional: test that it works locally
# download_emails("202001")


# In[ ]:


emails_rdd = sc.parallelize(dates).flatMap(download_emails).cache()


# In[ ]:


emails_rdd.count()


# In[ ]:


mailing_list_posts_mbox_df = emails_rdd.toDF(sampleRatio=1.0)


# In[ ]:


cached = mailing_list_posts_mbox_df.cache()


# In[ ]:


mailing_list_posts_mbox_df.select("list-id", "In-Reply-To").take(5)


# In[ ]:


spark_mailing_list_data = mailing_list_posts_mbox_df.filter(
    mailing_list_posts_mbox_df["list-id"].contains("spark")).repartition(60).cache()


# In[ ]:


spark_mailing_list_data.show()


# In[ ]:


spark_mailing_list_data.printSchema()


# In[ ]:


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


# In[ ]:


spark_mailing_list_data_with_date = spark_mailing_list_data.select(
    "*",
    extract_date_from_email_datefield_udf(spark_mailing_list_data["Date"]).alias("email_date"))


# In[ ]:


# Manually verify that our date parser is looking ok
spark_mailing_list_data.select(spark_mailing_list_data["Date"],
                               extract_date_from_email_datefield_udf(spark_mailing_list_data["Date"]).alias("email_date")
                              ).take(2)


# In[ ]:


mailing_list_posts_in_reply_to = spark_mailing_list_data_with_date.filter(
    spark_mailing_list_data["In-Reply-To"].isNotNull()).alias("mailing_list_posts_in_reply_to")
initial_posts = spark_mailing_list_data_with_date.filter(
    spark_mailing_list_data["In-Reply-To"].isNull()).alias("initial_posts").cache()


# In[ ]:


# See how many start-of-thread posts we have
initial_posts.count()


# In[ ]:


ids_in_reply = mailing_list_posts_in_reply_to.select("In-Reply-To", "message-id")


# In[ ]:


# Ok now it's time to save these
initial_posts.write.format("parquet").mode('overwrite').save(fs_prefix + "/initial_posts")
ids_in_reply.write.format("parquet").mode('overwrite').save(fs_prefix + "/ids_in_reply")


# In[ ]:


session.stop()


# In[ ]:




