#!/bin/bash


set -ex
# Hi friends! I'm the solution guide. If you get stuck I'm here to help
# Some other places you might want to look for help first:
# 1) 

# Optionally, toss a hand grenade in your current GCP setup with:
# ./cleanup.sh
# rm -rf $HOME
# surf to https://console.cloud.google.com/kubernetes/list
# and delete all the clusters.


echo "Download and run 'fast-start.sh'"
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/fast-start.sh
chmod +x fast-start.sh
./fast-start.sh
source ~/.bashrc
echo "OK... That seemed to go well."

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

