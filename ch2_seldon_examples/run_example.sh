#!/bin/bash
#tag::buildPipeline[]
dsl-compile --py train_pipeline.py --output job.yaml
kubectl apply --namespace kubeflow -f job.yaml
#end::buildPipeline[]
#tag::connectToWebUI[]
# If you're on minikube and not using a loadbalancer:
minikube service --url -n istio-system istio-ingressgateway
# If your on GCP https://<kf_app_name>.endpoints.<gcp_project_name>.cloud.goog/
# If you're on vanilla K8s
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].port}')

kubectl get svc istio-ingressgateway -n istio-system
#end::connectToWebUI[]
