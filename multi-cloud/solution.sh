#!/bin/bash

set -ex
# Hi friends! I'm the solution guide. If you get stuck I'm here to help
# Some other places you might want to look for help first:
# 1) 


echo "Setting up kubeflow project"
kfctl.sh init gcp_app --platform none
cd gcp_app
kfctl.sh generate k8s
kfctl.sh apply k8s

echo "Let's look at what's running:"
kubectl get all --all-namespaces

echo "Connecting to your kubeflow ambassador"
echo "Step 1) Setting up port forwarding"
kubectl port-forward svc/ambassador -n kubeflow 8080:80 &
echo "Now it's your turn to launch the cloudshell web preview to port 8080"

