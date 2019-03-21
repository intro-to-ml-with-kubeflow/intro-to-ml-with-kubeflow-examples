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

