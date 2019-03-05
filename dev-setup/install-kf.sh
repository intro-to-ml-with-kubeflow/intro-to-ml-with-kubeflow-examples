#!/bin/bash
#tag::install[]
#Configuration
export KUBEFLOW_DIR=~/kf_src
export KUBEFLOW_TAG=v0.4.1
# ^ You can also point this to master if you want to try
# Create the directory for Kubeflow to live in
mkdir -p $KUBEFLOW_DIR
pushd $KUBEFLOW_DIR
curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
# Optionally add the scripts directory to your path to simplify your work
export PATH=$PATH:$KUBEFLOW_DIR/scripts/
popd
#end::install[]
