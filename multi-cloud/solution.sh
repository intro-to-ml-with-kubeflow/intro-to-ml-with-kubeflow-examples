#!/bin/bash

set -ex
# Hi friends! I'm the solution guide. If you get stuck I'm here to help
# Some other places you might want to look for help first:
# 1) 


echo "Setting up kubeflow project"
export G_KF_APP=${G_KF_APP:="g-kf-app"}
pushd $G_KF_APP
source env.sh
# Normally we would have done platform & k8s generate/apply as well
kfctl.sh apply k8s


echo "Let's look at what's running:"
kubectl get all --all-namespaces

echo "Connecting to your kubeflow ambassador"
echo "Step 1) Setting up port forwarding"
kubectl port-forward svc/ambassador -n kubeflow 8080:80 &
echo "Now it's your turn to launch the cloudshell web preview to port 8080"

