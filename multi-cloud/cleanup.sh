#!/bin/bash

GZONE=${GZONE:="us-central1-a"} # For TPU access if we decide to go there
pushd gcp-app-kfctl
kfctl.sh delete k8s
kfctl.sh delete platform
popd

AZURE_CLUSTER_NAME=${AZURE_CLUSTER_NAME:="azure-kf-test"}
az aks delete --name AZURE_CLUSTER_NAME
