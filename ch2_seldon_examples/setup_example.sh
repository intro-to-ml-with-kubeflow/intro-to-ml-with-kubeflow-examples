#!/bin/bash

set -ex

echo "Setting up example"

unset ch2_example_path
ch2_example_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Using path ${ch2_example_path} for our example path"
example_path=$(dirname \"$0\")
#tag::generate_kf_app[]
# Pick the correct config file for your platform from
# https://github.com/kubeflow/manifests/tree/[version]/kfdef
# You can download & edit the configuration at this point if you need to.
# For generic k8s with istio:
export MANIFEST_BRANCH=${MANIFEST_BRANCH:-v1.0-branch}
export MANIFEST_VERSION=${MANIFEST_VERSION:-v1.0.1}
manifest_root=https://raw.githubusercontent.com/kubeflow/manifests/
# On most enviroments this will create a "vanilla" kubeflow install using istio.
KFDEF=${manifest_root}${MANIFEST_BRANCH}/kfdef/kfctl_k8s_istio.${MANIFEST_VERSION}.yaml
# On GCP this will create a cluster with basic authentication
if [ "$PLATFORM" == "gcp" ]; then
  KFDEF=${manifest_root}${MANIFEST_BRANCH}/kfdef/kfctl_gcp_iap.${MANIFEST_VERSION}.yaml
  # Set up IAP
  # TODO(holden)
  # Set up environment variables for GCP
  export PROJECT=${PROJECT:-"<your GCP project name>"}
  gcloud config set project ${PROJECT}
  export ZONE=${ZONE:-"<your GCP zone>"}
  gcloud config set compute/zone ${ZONE}
fi
pwd
export KF_PROJECT_NAME=${KF_PROJECT_NAME:-hello-kf-${PLATFORM}}
mkdir ${KF_PROJECT_NAME}
pushd ${KF_PROJECT_NAME}
# kfctl build -f $KFDEF -V
kfctl apply -f $KFDEF -V

popd
#end::generate_kf_app[]


# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
