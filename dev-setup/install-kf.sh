#!/bin/bash
#tag::install[]
#Configuration
export KUBEFLOW_DIR=~/kf_src
export KUBEFLOW_TAG=v0.4.0
# ^ You can also point this to master if you want to try
curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
# Optionally add the scripts directory to your path to simplify
export PATH=$PATH:$KUBEFLOW_DIR/scripts/
#end::install[]

