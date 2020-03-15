#!/bin/bash
set -ex
#tag::install[]
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
mkdir -p ~/bin
#Configuration
export KUBEFLOW_TAG=1.0
# ^ You can also point this to a different version if you want to try
KUBEFLOW_BASE="https://api.github.com/repos/kubeflow/kfctl/releases"
# TODO(holden): Verify if the hash in the file name is now part of the name or if that's just in the RC
KFCTL_URL=$(curl -s ${KUBEFLOW_BASE} |grep http | grep ${KUBEFLOW_TAG} |grep -i ${PLATFORM}| cut -d : -f 2,3 | tr -d '\" ' )
wget "${KFCTL_URL}"
KFCTL_FILE=$(echo ${KFCTL_URL##*/})
tar -xvf "${KFCTL_FILE}"
mv ./kfctl ~/bin/
rm "${KFCTL_FILE}"
# Optionally add the scripts directory to your path to simplify your work
export PATH=$PATH:~/bin
#end::install[]
