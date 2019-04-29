#!/usr/bin/env bash


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

