#!/bin/bash

set -ex

echo "Getting sudo cached..."
sudo ls
echo "Downloading Kubeflow"
export KUBEFLOW_SRC=~/kf
export KUBEFLOW_TAG=v0.4.1
mkdir -p $KUBEFLOW_SRC
pushd $KUBEFLOW_SRC
curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
echo "Adding to the path"
export KF_SCRIPTS=`pwd`/scripts
export PATH=$PATH:$KF_SCRIPTS
echo "export PATH=$PATH:$KF_SCRIPTS" >> ~/.bashrc

echo "Configuring Google default project if unset"

if [ ! GOOGLE_PROJECT=$(gcloud config get-value project 2>1 /dev/null) || -z "$GOOGLE_PROJECT"  ]; then
  echo "Default project not configured. Press enter to auto-configure or Ctrl-D to exit"
  echo "and change the project you're in up above (or manually set)"
  read configure
  latest_project=$(gcloud projects list | tail -n 1 | cut -f 1  -d' ')
  gcloud config set project $latest_project
fi
GOOGLE_PROJECT=$(gcloud config get-value project 2>1 /dev/null)

echo "Enabling Google Cloud APIs"
gcloud services enable file.googleapis.com storage-component.googleapis.com \
       storage-api.googleapis.com stackdriver.googleapis.com containerregistry.googleapis.com \
       iap.googleapis.com compute.googleapis.com container.googleapis.com
echo "Setting up Azure"
sudo apt-get install apt-transport-https lsb-release software-properties-common dirmngr -y
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
  sudo tee /etc/apt/sources.list.d/azure-cli.list
sudo apt-key --keyring /etc/apt/trusted.gpg.d/Microsoft.gpg adv \
     --keyserver packages.microsoft.com \
     --recv-keys BC528686B50D79E339D3721CEB3E94ADBE1229CF
sudo apt-get update
sudo apt-get install azure-cli
az login

echo "Starting up GKE cluster"
GZONE="us-central1-a" # For TPU access
GOOGLE_CLUSTER_NAME="google-kf-test"
gcloud beta container clusters create $GOOGLE_CLUSTER_NAME \
       --zone $GZONE \
       --machine-type "n1-standard-8" \
       --disk-type "pd-standard" \
       --disk-size "100" \
       --scopes "https://www.googleapis.com/auth/cloud-platform" \
       --addons HorizontalPodAutoscaling,HttpLoadBalancing \
       --enable-autoupgrade \
       --enable-autorepair \
       --enable-autoscaling --min-nodes 1 --max-nodes 10 --num-nodes 2 &
GCLUSTER_CREATION_PID=$!
echo "Starting up Azure K8s cluster"

echo "Connecting to google cluster"
wait $GCLUSTER_CREATION_PID || echo "cluster ready"
gcloud beta container clusters delete $GCLUSTER_NAME --zone $GZONE
