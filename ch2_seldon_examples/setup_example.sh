#!/bin/bash

set -ex

echo "Setting up example"

unset ch2_example_path
ch2_example_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Using path ${ch2_example_path} for our example path"
#tag::generate_kf_app[]
# Pick the correct config file for your platform from https://github.com/kubeflow/manifests/tree/[version]/kfdef
# And download it.
# You can edit the configuration at this point if you need to.
# For generic k8s with istio:
export MANIFEST_V=${MANIFEST_V:-v0.7-branch}
manifest_root=https://raw.githubusercontent.com/kubeflow/manifests/
KFDEF=${manifest_root}${MANIFEST_V}/kfdef/kfctl_k8s_istio.yaml
# For GCP
if [ "$PLATFORM" == "gcp" ]; then
  KFDEF=${manifest_root}${MANIFEST_V}/kfdef/kfctl_gcp_iap.yaml
fi
curl ${KFDEF} -o kfctl_kfdef.yaml
pwd
mkdir hello-kubeflow
pushd hello-kubeflow
kfctl build -V --file=../kfctl_kfdef.yaml
kfctl apply -V --file=../kfctl_kfdef.yaml
popd
#end::generate_kf_app[]

#install::seldon[]
# For now seldon needs to be installed with helm
#kubectl apply -f "${ch2_example_path}/tiller_rbac.yaml"
#helm init --service-account tiller
#kubectl rollout status deploy/tiller-deploy -n kube-system
#helm install seldon-core-operator --namespace kubeflow --repo https://storage.googleapis.com/seldon-charts --set usageMetrics.enabled=true --set istio.enabled=true
# We also need to make this accessiable to the pipeline user
#kubectl apply -f "${ch2_example_path}/pipeline_role.yaml"
#kubectl apply -f "${ch2_example_path}/pipeline_rolebinding.yaml"
#end::seldon[]


# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
