#!/bin/bash

example_path=$(dirname \"$0\")
#tag::generate_kf_app[]
# Pick the correct config file for your platform from https://github.com/kubeflow/manifests/tree/master/kfdef
# And download it.
# You can edit the configuration at this point if you need to.
# For generic k8s with istio:
wget https://raw.githubusercontent.com/kubeflow/manifests/master/kfdef/kfctl_k8s_istio.yaml
kfctl init hello-kubeflow --config kfctl_k8s_istio.yaml
pushd hello-kubeflow
kfctl generate all -V
# On GCP this will create a cluster
kfctl apply all -V
popd
#end::generate_kf_app[]

#install::seldon[]
# For now seldon needs to be installed with helm
kubectl apply -f ${example_path}/tiller_rbac.yaml
helm init --service-account tiller 
kubectl rollout status deploy/tiller-deploy -n kube-system
helm install seldon-core-operator --namespace kubeflow --repo https://storage.googleapis.com/seldon-charts --set usageMetrics.enabled=true --set istio.enabled=true
# We also need to make this accessiable to the pipeline user
kubectl apply -f ${example_path}/pipeline_role.yaml
kubectl apply -f ${example_path}/pipeline_rolebinding.yaml
#end::seldon[]


# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
