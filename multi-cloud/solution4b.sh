#!/usr/bin/env bash

cd ~/
git clone https://github.com/kubeflow/example-seldon

kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml

## The `-p build-push-image=true` doesn't work unless you have your own docker
## credentials stored in a K8s secret.
## So we build our image manually
docker build --force-rm=true -t skmnistclassifier_trainer:0.3 .
gcloud auth configure-docker
IMAGE_NAME="gcr.io/${GOOGLE_PROJECT}/skmnistclassifier_trainer:0.3"
docker tag skmnistclassifier_trainer:0.3 "${IMAGE_NAME}"
docker push "${IMAGE_NAME}"


cd example-seldon/workflows
argo submit training-sk-mnist-workflow.yaml -n kubeflow \
     -p build-push-image=false \
     -p docker-user="gcr.io/${GOOGLE_PROJECT}" \
     -p version=0.3
