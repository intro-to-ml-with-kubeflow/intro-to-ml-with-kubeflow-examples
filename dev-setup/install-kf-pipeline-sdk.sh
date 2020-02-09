#!/bin/bash
# Put as inside a venv
pushd /tmp
#tag::venv[]
virtualenv kfvenv --python python3
source kfvenv/bin/activate
#end::venv[]
popd
#tag::install[]
URL=https://storage.googleapis.com/ml-pipeline/release/latest/kfp.tar.gz
pip install "${URL}" --upgrade
#end::install[]
