    #!/bin/bash
set -ex
example_repo_home="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
KF_PLATFORM=${KF_PLATFORM:-minikube}
export KF_PLATFORM

if [ "$PLATFORM" == "gcp" ]; then
  # In GCP we also need a default zone
  gcloud config set compute/zone us-west1-b
fi

pushd dev-setup
command -v kfctl >/dev/null 2>&1 || source install-kf.sh
command -v kustomize >/dev/null 2>&1 || source install-kustomize.sh
source install-kf-pipeline-sdk.sh
popd
mkdir -p /tmp/abc
pushd /tmp/abc
source ${example_repo_home}/ch2_seldon_examples/setup_example.sh
popd
# rm -rf /tmp/abc
