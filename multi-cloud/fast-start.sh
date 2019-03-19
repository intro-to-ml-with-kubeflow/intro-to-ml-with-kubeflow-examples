#!/bin/bash

set -ex

echo "Getting sudo cached..."
sudo ls
echo "Setting up SSH if needed"
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    ssh-keygen
fi
echo "Downloading Kubeflow"
if [ ! -d ~/kf ]; then
  export KUBEFLOW_SRC=~/kf
  export KUBEFLOW_TAG=v0.4.1
  mkdir -p $KUBEFLOW_SRC
  pushd $KUBEFLOW_SRC
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
  echo "Adding to the path"
  export KF_SCRIPTS=`pwd`/scripts
  export PATH=$PATH:$KF_SCRIPTS
  echo "export PATH=\$PATH:$KF_SCRIPTS" >> ~/.bashrc
fi
echo "Downloading ksonnet"
export KSONNET_VERSION=0.11.0
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
if [ ! -d ks_0.11.0_${PLATFORM}_amd64 ]; then
  kubeflow_releases_base="https://github.com/ksonnet/ksonnet/releases/download"
  curl -OL "$kubeflow_releases_base/v${KSONNET_VERSION}/ks_${KSONNET_VERSION}_${PLATFORM}_amd64.tar.gz"
  tar zxf "ks_${KSONNET_VERSION}_${PLATFORM}_amd64.tar.gz"
  pwd=$(pwd)
  # Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
  export PATH=$PATH:"$pwd/ks_0.11.0_${PLATFORM}_amd64"
  echo "export PATH=\$PATH:$pwd/ks_0.11.0_${PLATFORM}_amd64" >> ~/.bashrc
fi


if ! command -v gcloud >/dev/null 2>&1; then
  export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
  echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
  sudo apt-get update && sudo apt-get install google-cloud-sdk
fi

echo "Configuring Google default project if unset"

if ! GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null) ||
     [ -z "$GOOGLE_PROJECT" ]; then
  echo "Default project not configured. Press enter to auto-configure or Ctrl-D to exit"
  echo "and change the project you're in up above (or manually set)"
  read configure
  latest_project=$(gcloud projects list | tail -n 1 | cut -f 1  -d' ')
  gcloud config set project $latest_project
  echo "gcloud config set project $latest_project" >> ~/.bashrc
fi
GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null)

echo "Enabling Google Cloud APIs"
gcloud services enable file.googleapis.com storage-component.googleapis.com \
       storage-api.googleapis.com stackdriver.googleapis.com containerregistry.googleapis.com \
       iap.googleapis.com compute.googleapis.com container.googleapis.com &
gke_api_enable_pid=$?
echo "Setting up Azure"
if ! command -v az >/dev/null 2>&1; then
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
fi

echo "Setting up Azure resource group"
az configure --defaults location=westus
az group exists -n kf-westus || az group create -n kf-westus

echo "Starting up GKE cluster"
wait $gke_api_enable_pid || echo "API enable command already finished"
GZONE=${GZONE:="us-central1-a"} # For TPU access if we decide to go there
GOOGLE_CLUSTER_NAME=${GOOGLE_CLUSTER_NAME:="google-kf-test"}
gcloud beta container clusters describe $GOOGLE_CLUSTER_NAME --zone $GZONE || gcloud beta container clusters create $GOOGLE_CLUSTER_NAME \
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
az configure --defaults location=westus
az group exists -n kf-westus || az group create -n kf-westus
AZURE_CLUSTER_NAME=${AZURE_CLUSTER_NAME:="azure-kf-test"}
az aks show -g kf-westus -n $AZURE_CLUSTER_NAME || az aks create --name $AZURE_CLUSTER_NAME \
   --resource-group kf-westus \
   --node-count 2 \
   --ssh-key-value ~/.ssh/id_rsa.pub \
   --node-osdisk-size 30 &
AZURE_CLUSTER_CREATION_PID=$!

echo "Creating kubeflow project"

echo "Connecting to google cluster"
wait $GCLUSTER_CREATION_PID || echo "google cluster ready"
gcloud container clusters get-credentials $GOOGLE_CLUSTER_NAME --zone $GZONE

echo "When you are ready to connect to your Azure cluster run:"
echo "az aks get-credentials --name azure-kf-test --resource-group westus"
