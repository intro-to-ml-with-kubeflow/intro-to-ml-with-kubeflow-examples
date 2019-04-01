#!/bin/bash
#tag::work[]
export KUBEFLOW_TAG=v0.4.1
curl -O https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/setup-minikube.sh
chmod +x setup-minikube.sh
./setup-minikube.sh
#end::work[]
