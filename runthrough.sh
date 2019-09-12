#!/bin/bash
set -ex
example_home=$(pwd)
KF_PLATFORM=minikube
explort KF_PLATFORM
pushd dev-setup
source install-kf.sh
source install-kustomize.sh
source install-kf-pipeline-sdk.sh
popd
mkdir -p /tmp/abc
pushd /tmp/abc
source ${example_home}/ch2_seldon_examples/setup_example.sh
popd
# rm -rf /tmp/abc
