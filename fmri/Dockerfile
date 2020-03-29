FROM gcr.io/spark-operator/spark:v2.4.5
COPY dsvd/target/dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar /
CMD mkdir data
COPY dsvd/s.csv /data/s.csv
ENTRYPOINT ["/opt/entrypoint.sh"]