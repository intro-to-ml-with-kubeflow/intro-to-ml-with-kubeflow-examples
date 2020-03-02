#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Yes we need both these imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import *
from pyspark.sql.types import StructField, StructType
from pyspark.sql.catalog import UserDefinedFunction
import os


# In[ ]:





# In[4]:


fs_prefix = "s3a://kf-book-examples/mailing-lists" # Create with mc as in ch1


# In[5]:


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
                   "gcr.io/boos-demo-projects-are-rad/kubeflow/spark-worker/spark-py-36:v3.0.0-preview2-23")
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


# In[6]:


# Data fetch pipeline: Download mailing list data


# In[7]:


list_name="spark-user"


# In[8]:


mailing_list_template="http://mail-archives.apache.org/mod_mbox/{list_name}/{date}.mbox"


# In[9]:


# Generate the possible dates


# In[10]:


start_year=2019 # Change to 2002 once you've verified
end_year=2021
dates = ["{:d}{:02d}".format(year, month) for year in range(start_year, end_year) for month in range (1,12)]


# In[11]:


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


# In[12]:


# Optional: test that it works locally
# download_emails("202001")


# In[13]:


emails_rdd = sc.parallelize(dates).flatMap(download_emails).cache()


# In[14]:


emails_rdd.count()


# In[15]:


mailing_list_posts_mbox_df = emails_rdd.toDF(sampleRatio=1.0)


# In[16]:


cached = mailing_list_posts_mbox_df.cache()


# In[17]:


mailing_list_posts_mbox_df.select("list-id", "In-Reply-To").take(5)


# In[18]:


spark_mailing_list_data = mailing_list_posts_mbox_df.filter(
    mailing_list_posts_mbox_df["list-id"].contains("spark")).repartition(60).cache()


# In[19]:


spark_mailing_list_data.show()


# In[20]:


spark_mailing_list_data.printSchema()


# In[21]:


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


# In[22]:


spark_mailing_list_data_with_date = spark_mailing_list_data.select(
    "*",
    extract_date_from_email_datefield_udf(spark_mailing_list_data["Date"]).alias("email_date"))


# In[23]:


# Manually verify that our date parser is looking ok
spark_mailing_list_data.select(spark_mailing_list_data["Date"],
                               extract_date_from_email_datefield_udf(spark_mailing_list_data["Date"]).alias("email_date")
                              ).take(2)


# In[24]:


mailing_list_posts_in_reply_to = spark_mailing_list_data_with_date.filter(
    spark_mailing_list_data["In-Reply-To"].isNotNull()).alias("mailing_list_posts_in_reply_to")
initial_posts = spark_mailing_list_data_with_date.filter(
    spark_mailing_list_data["In-Reply-To"].isNull()).alias("initial_posts").cache()


# In[25]:


# See how many start-of-thread posts we have
initial_posts.count()


# In[26]:


ids_in_reply = mailing_list_posts_in_reply_to.select("In-Reply-To", "message-id")


# In[27]:


# Ok now it's time to save these
initial_posts.write.format("parquet").mode('overwrite').save(fs_prefix + "/initial_posts")
ids_in_reply.write.format("parquet").mode('overwrite').save(fs_prefix + "/ids_in_reply")


# In[28]:


session.stop()


# In[ ]:




