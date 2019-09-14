#!/bin/bash

example_path=$(dirname \"$0\")
#tag::generate_kf_app[]
# Platform can be one of: aws,gcp, or minikube
# You can leave off --platform for a vanilla distribution
# On gcp add --project [nameofproject]
kfctl init hello-kubeflow --platform $KF_PLATFORM $KF_PROJ
echo "For now we need to hack the app.yaml :("
exit 1
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

## TODO check if nfs-1 exists before trying to create
#tag::createPV[]
export NAMESPACE=kubeflow
# TODO move this into the pipeline
kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/ch2_seldon_examples/pv-volume.yaml -n $NAMESPACE
kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/ch2_seldon_examples/pv-claim.yaml -n $NAMESPACE
#end::createPV[]
