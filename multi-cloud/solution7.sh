#!/usr/bin/env bash

# Adding hacky transporter for moving model from GCP to IBMCloud

gcloud auth configure-docker

mkdir hacky-s3
cd hacky-s3
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/Dockerfile
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/beam-me-up-scotty.py
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/requirements.txt

gcloud auth configure-docker
GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null)
##

docker build -t gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord .
docker push gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord

wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/hacky-s3-copy.yaml

kubectl create -f hacky-s3-copy.yaml -n kubeflow
