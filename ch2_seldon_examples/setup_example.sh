#!/bin/bash

set -ex

echo "Setting up example"

unset ch2_example_path
ch2_example_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Using path ${ch2_example_path} for our example path"
example_path=$(dirname ${ch2_example_path})
#tag::generate_kf_app_p1[]
# Pick the correct config file for your platform from
# https://github.com/kubeflow/manifests/tree/[version]/kfdef
# You can download & edit the configuration at this point if you need to.
# For generic k8s with istio:
export MANIFEST_BRANCH=${MANIFEST_BRANCH:-v1.0-branch}
export MANIFEST_VERSION=${MANIFEST_VERSION:-v1.0.1}

export KF_PROJECT_NAME=${KF_PROJECT_NAME:-hello-kf-${PLATFORM}}
mkdir ${KF_PROJECT_NAME}
pushd ${KF_PROJECT_NAME}

manifest_root=https://raw.githubusercontent.com/kubeflow/manifests/
# On most enviroments this will create a "vanilla" kubeflow install using istio.
KFDEF=${manifest_root}${MANIFEST_BRANCH}/kfdef/kfctl_k8s_istio.${MANIFEST_VERSION}.yaml
#end::generate_kf_app_p1[]
# On GCP this will create a cluster with basic authentication
if [ "$PLATFORM" == "gcp" ]; then
  KFDEF=${manifest_root}${MANIFEST_BRANCH}/kfdef/kfctl_gcp_iap.${MANIFEST_VERSION}.yaml
  # Temp hack
  cp ${example_path}/kfctl_gcp_iap.v1.0.1.yaml ./
  KFDEF=./kfctl_gcp_iap.v1.0.1.yaml
  # Set up IAP
  # TODO(holden)
  # Set up environment variables for GCP
  export PROJECT=${PROJECT:-"<your GCP project name>"}
  gcloud config set project ${PROJECT}
  export ZONE=${ZONE:-"<your GCP zone>"}
  gcloud config set compute/zone ${ZONE}
fi
pwd
#tag::generate_kf_app_p2[]
kfctl apply -f $KFDEF -V

popd
#end::generate_kf_app_p2[]


# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
