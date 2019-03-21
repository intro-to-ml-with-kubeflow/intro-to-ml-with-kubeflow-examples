#!/usr/bin/env bash

cd ~/
git clone https://github.com/kubeflow/example-seldon

kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml

cd example-seldon/workflows
argo submit training-sk-mnist-workflow.yaml -n kubeflow -p build-push-image=true

