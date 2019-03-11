#!/bin/bash

#tag::generate_kf_app[]
# Platform can be one of: minikube, gcp, docker-for-desktop, ack, or null/none/generic
kfctl.sh init first_example_project --platform none
pushd first_example_project
source env.sh
kfctl.sh generate k8s
kfctl.sh apply k8s
pushd ks_app
#end::generate_kf_app[]

#tag::setup_components[]
# Set up Helm
kubectl -n kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
kubectl rollout status deploy/tiller-deploy -n kube-system
# Setup SAD
helm install seldon-core-analytics --name seldon-core-analytics --set grafana_prom_admin_password=password --set persistence.enabled=false --repo https://storage.googleapis.com/seldon-charts --namespace kubeflow
#end::setup_components[]


## TODO check if nfs-1 exists before trying to create
#tag::createPV[]
kubectl create -f ch2_seldon_examples/pv-volume.yaml -n $NAMESPACE
kubectl create -f ch2_seldon_examples/pv-claim.yaml -n $NAMESPACE
#end:createPV[]

# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]
