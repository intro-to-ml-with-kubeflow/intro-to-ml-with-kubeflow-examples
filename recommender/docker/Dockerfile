FROM  tensorflow/tensorflow:1.15.0-py3
RUN pip3 install --upgrade pip
RUN pip3 install pandas --upgrade
RUN pip3 install keras --upgrade
RUN pip3 install minio --upgrade
RUN pip3 install kubernetes --upgrade
RUN pip3 install kfmd --upgrade

RUN mkdir -p /opt/kubeflow
COPY Recommender_Kubeflow.py /opt/kubeflow/
ENTRYPOINT ["python3", "/opt/kubeflow/Recommender_Kubeflow.py"]