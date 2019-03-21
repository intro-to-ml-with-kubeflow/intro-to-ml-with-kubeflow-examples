#!/bin/bash

set -ex

echo "Getting sudo cached..."
sudo ls
echo "Setting up SSH if needed"
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    ssh-keygen
fi
echo "Installing some dependencies"
pip install --user pyyaml
echo "Downloading Kubeflow"
export KUBEFLOW_SRC=~/kf
export KUBEFLOW_TAG=v0.4.1
export KF_SCRIPTS=$KUBEFLOW_SRC/scripts
export PATH=$PATH:$KF_SCRIPTS
if [ ! -d ~/kf ]; then
  mkdir -p $KUBEFLOW_SRC
  pushd $KUBEFLOW_SRC
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
  echo "export PATH=\$PATH:$KF_SCRIPTS" >> ~/.bashrc
  popd
fi
echo "Adding to the path"

echo "Downloading ksonnet"
export KSONNET_VERSION=0.11.0
PLATFORM=$(uname | tr '[:upper:]' '[:lower:]') # Either linux or darwin
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

#echo "Enabling Google Cloud APIs async for speedup"
gcloud services enable file.googleapis.com storage-component.googleapis.com \
       storage-api.googleapis.com stackdriver.googleapis.com containerregistry.googleapis.com \
       iap.googleapis.com compute.googleapis.com container.googleapis.com
gke_api_enable_pid=$?
if [ ! -z "$SKIP_AZURE" ]; then
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
fi
  
echo "Creating Google Kubeflow project:"
export G_KF_APP=${G_KF_APP:="g-kf-app"}
export ZONE=${ZONE:="us-central1-a"}
export GZONE=$ZONE
echo "export G_KF_APP=$G_KF_APP" >> ~/.bashrc
kfctl.sh init ${G_KF_APP} --platform gcp
pushd $G_KF_APP
source env.sh
if [[ -z "$CLIENT_ID" ]]; then
  export CLIENT_ID=${CLIENT_ID:="fake_client_id"}
  export CLIENT_SECRET=${CLIENT_SECRET:="fake_client_secret"}
  export SKIP_IAP="true"
fi
kfctl.sh generate platform
kfctl.sh apply platform &
APPLY_GCP_PLATFORM_PID=$!
kfctl.sh generate k8s
# Disabling IAP IAM check
echo "Skip IAP if we aren't set up for it"
if [[ ! -z "$SKIP_IAP" ]]; then
  pushd ks_app
  # Disable IAP check in Jupyter Hub
  ks param set jupyter jupyterHubAuthenticator null
  popd
fi
popd


if [[ ! -z "$SKIP_AZURE" ]]; then
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
fi


echo "Connecting to google cluster"
wait $APPLY_GCP_PLATFORM_PID || echo "GCP cluster ready"
gcloud container clusters get-credentials ${G_KF_APP} --zone $GZONE

echo "When you are ready to connect to your Azure cluster run:"
echo "az aks get-credentials --name azure-kf-test --resource-group westus"
