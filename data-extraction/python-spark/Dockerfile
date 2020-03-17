# Use the spark operator image as base
FROM gcr.io/spark-operator/spark-py:v2.4.5
# Install Python requirements
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
# Now you can reference local:///job/my_file.py
RUN mkdir -p /job
COPY *.py /job

ENTRYPOINT ["/opt/entrypoint.sh"]