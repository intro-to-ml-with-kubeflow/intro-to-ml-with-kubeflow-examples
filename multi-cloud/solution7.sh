#!/usr/bin/env bash

# Adding hacky transporter for moving model from GCP to IBMCloud

gcloud auth configure-docker

mkdir hacky-s3
cd hacky-s3
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/Dockerfile
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/beam-me-up-scotty.py
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/requirements.txt

echo "You are going to need to edit beam-up-scotty.py to point to your creds."
echo "Press enter when done!"
# shellcheck disable=2034
read -r panda


gcloud auth configure-docker
GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null)
##

docker build -t "gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord" .
docker push "gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord"

wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/hacky-s3-copy/hacky-s3-copy.yaml

echo "Yay now, your going to need to edit hacky-s3-copy.yaml to point to your GOOGLE_PROJECT"
echo "Press enter when done"
# shellcheck disable=2034
read -r panda


kubectl create -f hacky-s3-copy.yaml -n kubeflow
echo "If you hit an error about image not found, make sure you made your GCP container repo public"
