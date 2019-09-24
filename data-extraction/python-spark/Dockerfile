# Use the spark operator 
FROM gcr.io/spark-operator/spark:v2.4.4
COPY requirements.txt /
RUN virtualenv --python python3 /myvenv
RUN source /myvenv/bin/activate && pip install -r /requirements.txt
RUN mkdir -p /job
COPY *.py /job

ENTRYPOINT ["/opt/entrypoint.sh"]