FROM gcr.io/spark-operator/spark:v2.4.5-gcs-prometheus

COPY target/covid-0.1-jar-with-dependencies.jar /

## Someday soon we'll live in a world where this hack is unnessecary
# https://github.com/GoogleCloudDataproc/hadoop-connectors/issues/323
CMD rm /opt/spark/jars/gcs-connector-latest-hadoop2.jar
ADD https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop2-2.0.1.jar $SPARK_HOME/jars

ENTRYPOINT ["/opt/entrypoint.sh"]
