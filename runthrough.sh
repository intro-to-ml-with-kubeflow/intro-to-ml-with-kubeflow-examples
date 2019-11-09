#!/bin/bash
set -ex
example_repo_home="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
KF_PLATFORM=${KF_PLATFORM:-minikube}

export KF_PLATFORM
pushd dev-setup
# Skip for now since we need 0.7
source install-kf.sh
source install-kustomize.sh
source install-kf-pipeline-sdk.sh
popd
mkdir -p /tmp/abc
pushd /tmp/abc
${example_repo_home}/ch2_seldon_examples/setup_example.sh
popd
# rm -rf /tmp/abc
