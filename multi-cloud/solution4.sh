#!/usr/bin/env bash

cd ~/
git clone https://github.com/kubeflow/example-seldon

kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml

## The `-p build-push-image=true` doesn't work unless you have your own docker
## credentials stored in a K8s secret. Instead if you made a custom docker image you
## can look at solution4b.sh

cd example-seldon/workflows
argo submit training-sk-mnist-workflow.yaml -n kubeflow -p build-push-image=false
