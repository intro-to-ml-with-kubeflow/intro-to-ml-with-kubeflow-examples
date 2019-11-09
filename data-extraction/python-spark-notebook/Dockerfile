# See https://www.kubeflow.org/docs/notebooks/custom-notebook/
ARG base
FROM $base

# Set an enviroment variable for where we are going to put spark
ENV SPARK_HOME /opt/spark

# Install java because Spark needs it
RUN apt-get update && apt-get install -yq openjdk-8-jdk && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install Spark
RUN set -ex && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh

ADD  https://www-us.apache.org/dist/spark/spark-2.4.4/spark-2.4.4-bin-hadoop2.7.tgz /tmp/
RUN  cd /opt && tar -xvf /tmp/spark-2.4.4-bin-hadoop2.7.tgz && mv spark-2.4.4-bin-hadoop2.7 spark && cd spark/python && pip install -e .
# Install some useful libraries
RUN pip install pandas pyarrow==0.11.0 spacy

WORKDIR /opt/spark/work-dir
RUN chmod g+w /opt/spark/work-dir

# Add access to GCS
RUN rm $SPARK_HOME/jars/guava-14.0.1.jar
ADD http://central.maven.org/maven2/com/google/guava/guava/23.0/guava-23.0.jar $SPARK_HOME/jars
# Add the connector jar needed to access Google Cloud Storage using the Hadoop FileSystem API.
ADD https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-latest-hadoop2.jar $SPARK_HOME/jars
