#!/bin/bash

set -ex

echo "Downloading Kubeflow"
export KUBEFLOW_SRC=~/kf
export KUBEFLOW_TAG=v0.4.1
mkdir -p $KUBEFLOW_SRC
pushd $KUBEFLOW_SRC
curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
export KF_SCRIPTS=`pwd`/scrtips

echo "export PATH=$PATH:$KF_SCRIPTS" >> ~/.bashrc

echo "Setting up GKE & file APIs"
gcloud 
echo "Setting up Azure"
curl -L https://aka.ms/InstallAzureCli | bash
az login
