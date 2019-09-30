#!/bin/bash
set -ex
example_home=$(pwd)
KF_PLATFORM=${KF_PLATFORM:-minikube}

export KF_PLATFORM
pushd dev-setup
# Skip for now since we need 0.7
# source install-kf.sh
source install-kustomize.sh
source install-kf-pipeline-sdk.sh
popd
mkdir -p /tmp/abc
pushd /tmp/abc
source ${example_home}/ch2_seldon_examples/setup_example.sh
popd
# rm -rf /tmp/abc
