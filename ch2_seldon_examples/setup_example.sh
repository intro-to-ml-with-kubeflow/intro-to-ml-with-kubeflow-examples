#!/bin/bash


#tag::generate_kf_app[]
# Platform can be one of: minikube, gcp, docker-for-desktop, ack, or null/none/generic
kfctl.sh init hello_kubeflow --platform none
pushd hello_kubeflow
source env.sh
kfctl.sh generate k8s
pushd ks_app
## Install Seldon
ks param set ambassador ambassadorServiceType NodePort
ks pkg install kubeflow/seldon
ks generate seldon seldon
ks apply default -c seldon
## end install seldon
popd
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
helm install seldon-core-analytics \
	--name seldon-core-analytics \
	--set grafana_prom_admin_password=password \
	--set persistence.enabled=false \
	--repo https://storage.googleapis.com/seldon-charts \
	--namespace kubeflow
#end::setup_components[]

# TODO(trevor): what version/tag?
#tag::cloneSeldonExample[]
# Clone the base seldon example
cd ~/
git clone https://github.com/kubeflow/example-seldon
#end::cloneSeldonExample[]

## TODO check if nfs-1 exists before trying to create
#tag::createPV[]
export NAMESPACE=kubeflow
# TODO change these to oreilly target
kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/ch2_seldon_examples/pv-volume.yaml -n $NAMESPACE
kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/ch2_seldon_examples/pv-claim.yaml -n $NAMESPACE
#end::createPV[]


