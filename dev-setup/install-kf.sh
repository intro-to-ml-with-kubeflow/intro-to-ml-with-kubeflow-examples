#!/bin/bash
#tag::install[]
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
mkdir -p ~/bin
#Configuration
export KUBEFLOW_TAG=v1.0.0-rc4
# ^ You can also point this to a different version if you want to try
KUBEFLOW_BASE="https://github.com/kubeflow/kfctl/releases/download"
# TODO(holden): Verify if the hash in the file name is now part of the name or if that's just in the RC
KUBEFLOW_FILE="kfctl_${KUBEFLOW_TAG}_${PLATFORM}.tar.gz"
wget "${KUBEFLOW_BASE}/${KUBEFLOW_TAG}/${KUBEFLOW_FILE}"
tar -xvf "${KUBEFLOW_FILE}"
mv ./kfctl ~/bin/
rm "${KUBEFLOW_FILE}"
# Optionally add the scripts directory to your path to simplify your work
export PATH=$PATH:~/bin
#end::install[]
