# from https://github.com/flmu/mlflow-tracking-server

FROM python:3.7

RUN pip3 install --upgrade pip && \
    pip3 install mlflow --upgrade && \
    pip3 install awscli --upgrade  && \
    pip3 install boto3 --upgrade

ENV PORT 5000
ENV AWS_BUCKET bucket
ENV AWS_ACCESS_KEY_ID aws_id
ENV AWS_SECRET_ACCESS_KEY aws_key

ENV FILE_DIR /tmp/mlflow

RUN mkdir -p /opt/mlflow

COPY run.sh /opt/mlflow
RUN chmod -R 777 /opt/mlflow/

ENTRYPOINT ["/opt/mlflow/run.sh"]