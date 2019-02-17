#!/bin/bash
#tag::installmicrok8s[]
sudo snap install microk8s --classic
#end::installmicrok8s[]
#tag::bootstrapwithcanonicallabs[]
git clone https://github.com/canonical-labs/kubeflow-tools
cd kubeflow-tools
KUBEFLOW_VERSION=0.4.1 ./install-kubeflow.sh
#end::bootstrapwithcanonicallabs[]
