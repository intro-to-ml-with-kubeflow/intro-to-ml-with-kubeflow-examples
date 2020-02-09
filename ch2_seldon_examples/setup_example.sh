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
export MANIFEST_V=${MANIFEST_V:-v0.7-branch}
manifest_root=https://raw.githubusercontent.com/kubeflow/manifests/
KFDEF=${manifest_root}${MANIFEST_V}/kfdef/kfctl_k8s_istio.yaml
# For GCP
if [ "$PLATFORM" == "gcp" ]; then
  KFDEF=${manifest_root}${MANIFEST_V}/kfdef/kfctl_gcp_basic_auth.0.7.1.yaml
  # Set up environment variables for GCP
  export PROJECT=<your GCP project ID>
  gcloud config set project ${PROJECT}
  export ZONE=<your GCP zone>
  gcloud config set compute/zone ${ZONE}

  # Configure username and password for basic authentication
  export KUBEFLOW_USERNAME=<your username>
  export KUBEFLOW_PASSWORD=<your password>
fi
pwd
mkdir hello-kubeflow
pushd hello-kubeflow
# On GCP this will create a cluster with basic authentication
kfctl apply -f $KFDEF -V

popd
#end::generate_kf_app[]


# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
