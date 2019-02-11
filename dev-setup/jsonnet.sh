#!/bin/bash
set -e
set -x
#tag::snap[]
sudo snap install jsonnet
#end::snap[]
#tag::manual[]
export JSONNET_VERSION=0.12.1
wget https://github.com/google/jsonnet/archive/v$JSONNET_VERSION.tar.gz
# You will need to add this to your path if it is not already
tar -xvf v$JSONNET_VERSION.tar.gz
cd jsonnet-$JSONNET_VERSION
make
# Or otherwise add to your path
sudo cp jsonent /usr/bin/
#end::manual[]
