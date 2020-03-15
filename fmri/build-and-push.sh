#!/bin/bash
if [ ! -f dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar ]; then
  wget https://github.com/intro-to-ml-with-kubeflow/hacky-bins/raw/master/dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar
fi
IMAGE="${CONTAINER_REGISTRY}/kubeflow/spark-with-dsvd:v1"
docker build  -t ${IMAGE} -f Dockerfile .
docker push ${IMAGE}
