#!/bin/bash
#tag::install[]
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
mkdir -p ~/bin
#Configuration
export KUBEFLOW_TAG=v0.6.2
# ^ You can also point this to a different version if you want to try
KUBEFLOW_BASE="https://github.com/kubeflow/kubeflow/releases/download"
KUBEFLOW_FILE="kfctl_${KUBEFLOW_TAG}_${PLATFORM}.tar.gz"
wget "${KUBEFLOW_BASE}/${KUBEFLOW_TAG}/${KUBEFLOW_FILE}"
tar -xvf "${KUBEFLOW_FILE}"
mv ./kfctl ~/bin/
rm "${KUBEFLOW_FILE}"
# Optionally add the scripts directory to your path to simplify your work
export PATH=$PATH:~/bin
#end::install[]
