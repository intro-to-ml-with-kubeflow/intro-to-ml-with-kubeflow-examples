#!/usr/bin/env bash

## Adding Seldon

# Now we install some extra components, which we need to do in the KS app directory
# We'll install seldon on Google for serving (don't worry we'll do it again elsewhere)
pushd ks_app
ks pkg install kubeflow/seldon
ks generate seldon seldon
ks apply default -c seldon
popd
# Applying to the cluster is done with kfctl.sh (although you could use ks directly too)
kfctl.sh apply k8s
# Optionally there are additional seldon components, like the analytics

## Install Argo
curl -sSL -o ~/argo https://github.com/argoproj/argo/releases/download/v2.2.1/argo-linux-amd64
chmod +x ~/argo
kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.2.1/manifests/install.yaml
kubectl create clusterrolebinding YOURNAME-cluster-admin-binding --clusterrole=cluster-admin --user=YOUREMAIL@gmail.com
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default
kubectl create clusterrolebinding sa-admin --clusterrole=cluster-admin --serviceaccount=kubeflow:default




## Move this later (optional task)
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

