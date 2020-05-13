#!/bin/bash

CONTAINER_REGISTRY=docker.io
if [ ! -f dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar ]; then
  wget https://github.com/intro-to-ml-with-kubeflow/hacky-bins/raw/master/dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar
fi
IMAGE="${CONTAINER_REGISTRY}/rawkintrevo/spark-with-dsvd:0.0.4"
docker build  -t ${IMAGE} -f Dockerfile .
docker push ${IMAGE}
