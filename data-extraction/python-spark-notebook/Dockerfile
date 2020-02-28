# See https://www.kubeflow.org/docs/notebooks/custom-notebook/
ARG base
FROM $base
ARG sparkversion
ARG sparkrelease
# We need to run as root for updates
USER root

# Set an enviroment variable for where we are going to put spark
ENV SPARK_HOME /opt/spark

# Install java because Spark needs it
RUN apt-get update && \
    apt-get install -yq openjdk-8-jre openjdk-8-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Spark
RUN set -ex && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh

RUN  echo "Setting up $sparkversion"
RUN  cd /tmp && \
     (wget https://www-us.apache.org/dist/spark/spark-${sparkversion}/${sparkrelease}.tgz || wget https://www-eu.apache.org/dist/spark/spark-${sparkversion}/${sparkrelease}.tgz) && \
     cd /opt && tar -xvf /tmp/${sparkrelease}.tgz && rm /tmp/${sparkrelease}.tgz && mv ${sparkrelease} spark && cd spark/python && pip install -e .

# Add access to GCS
RUN rm $SPARK_HOME/jars/guava-1*.jar
ADD https://maven-central.storage.googleapis.com/maven2/com/google/guava/guava/23.0/guava-23.0.jar $SPARK_HOME/jars
# Add the connector jar needed to access Google Cloud Storage using the Hadoop FileSystem API.
ADD https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-latest-hadoop3.jar $SPARK_HOME/jars

# Add the S3A connector
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.732/aws-java-sdk-bundle-1.11.732.jar $SPARK_HOME/jars

# Fix permissions
WORKDIR /opt/spark/work-dir
RUN chmod -R 777 /opt/spark/


# Switch the user back, using jovyan as a user is bad but the base image
# depends on it.
USER jovyan