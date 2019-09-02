#!/bin/bash
set -ex
pushd dev-setup
source install-kf.sh
source install-kustomize.sh
popd
mkdir -p /tmp/abc
pushd /tmp/abc
kfctl init boop
popd
rm -rf /tmp/abc
