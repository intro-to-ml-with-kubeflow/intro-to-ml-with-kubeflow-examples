#!/bin/bash

# Long story, buy me a drink, we modify the PATH in here in previous installs.
source ~/.bashrc

set -ex

if [[ -z "$SKIP_AZURE" ]]; then
  export IF_AZURE="& Azure"
fi

echo "Prepairing to set up I will be deploying on GCP${IF_AZURE}"
echo "Press enter if this OK or ctrl-d to change the settings"
echo "Azure is controlled with the SKIP_AZURE env variable"
echo "p.s. did you remember to run me with tee?"
read panda

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
export KSONNET_VERSION=0.13.1
PLATFORM=$(uname | tr '[:upper:]' '[:lower:]') # Either linux or darwin
export PLATFORM
if [ ! -d ks_${KSONNET_VERSION}_${PLATFORM}_amd64 ]; then
  kubeflow_releases_base="https://github.com/ksonnet/ksonnet/releases/download"
  curl -OL "$kubeflow_releases_base/v${KSONNET_VERSION}/ks_${KSONNET_VERSION}_${PLATFORM}_amd64.tar.gz"
  tar zxf "ks_${KSONNET_VERSION}_${PLATFORM}_amd64.tar.gz"
  pwd=$(pwd)
  # Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
  export PATH=$PATH:"$pwd/ks_${KSONNET_VERSION}_${PLATFORM}_amd64"
  echo "export PATH=\$PATH:$pwd/ks_${KSONNET_VERSION}_${PLATFORM}_amd64" >> ~/.bashrc
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
echo "export GOOGLE_PROJECT=$GOOGLE_PROJECT" >> ~/.bashrc


echo "Enabling Google Cloud APIs async for speedup"
gcloud services enable file.googleapis.com storage-component.googleapis.com \
       storage-api.googleapis.com stackdriver.googleapis.com containerregistry.googleapis.com \
       iap.googleapis.com compute.googleapis.com container.googleapis.com &
gke_api_enable_pid=$?
if [[ -z "$SKIP_AZURE" ]]; then
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
else
  echo "Skipping Azure setup since configured as such"
fi


echo "Creating bucket"
export BUCKET_NAME=kubeflow-${GOOGLE_PROJECT}
echo "export BUCKET_NAME=kubeflow-${GOOGLE_PROJECT}" >> ~/.bashrc
gsutil mb -c regional -l us-central1 gs://${BUCKET_NAME} || echo "Bucket exists"

echo "Creating Google Kubeflow project:"
export G_KF_APP=${G_KF_APP:="g-kf-app"}
export ZONE=${ZONE:="us-central1-a"}
export GZONE=$ZONE
echo "export G_KF_APP=$G_KF_APP" >> ~/.bashrc
kfctl.sh init ${G_KF_APP} --platform gcp
pushd ${G_KF_APP}
source env.sh
if [[ -z "$CLIENT_ID" ]]; then
  export CLIENT_ID=${CLIENT_ID:="fake_client_id"}
  export CLIENT_SECRET=${CLIENT_SECRET:="fake_client_secret"}
  export SKIP_IAP="true"
fi
kfctl.sh generate platform
echo "Waiting on enabling just to avoid race conditions"
wait $gke_api_enable_pid || echo "Services already enabled"
echo "Apply the platform. Sometimes the deployment manager behaves weirdly so retry"
kfctl.sh apply platform || (echo "retrying platform application" && kfctl.sh apply platform)
APPLY_GCP_PLATFORM_PID=$!
popd

if [[ -z "$SKIP_AZURE" ]]; then
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

pushd ${G_KF_APP}
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


echo "Connecting to google cluster"
wait $APPLY_GCP_PLATFORM_PID || echo "GCP cluster ready"
echo "Creating SA creds now that platform has settled"
echo "Setting up a GCP-SA for storage"
export SERVICE_ACCOUNT=user-gcp-sa
export SERVICE_ACCOUNT_EMAIL=${SERVICE_ACCOUNT}@${GOOGLE_PROJECT}.iam.gserviceaccount.com
export STORAGE_SERVICE_ACCOUNT=user-gcp-sa-storage
export STORAGE_SERVICE_ACCOUNT_EMAIL=${STORAGE_SERVICE_ACCOUNT}@${GOOGLE_PROJECT}.iam.gserviceaccount.com
export KEY_FILE=${HOME}/secrets/${STORAGE_SERVICE_ACCOUNT_EMAIL}.json

if [ ! -f ${KEY_FILE} ]; then
  echo "Creating GCP SA storage account"
  echo "
export STORAGE_SERVICE_ACCOUNT=user-gcp-sa-storage
export STORAGE_SERVICE_ACCOUNT_EMAIL=${STORAGE_SERVICE_ACCOUNT}@${GOOGLE_PROJECT}.iam.gserviceaccount.com
" >> ~/.bashrc
  gcloud iam service-accounts create ${STORAGE_SERVICE_ACCOUNT} \
	 --display-name "GCP Service Account for use with kubeflow examples" || echo "SA exists, just modifying"

  gcloud projects add-iam-policy-binding ${GOOGLE_PROJECT} --member \
	 serviceAccount:${STORAGE_SERVICE_ACCOUNT_EMAIL} \
	 --role=roles/storage.admin
  gcloud iam service-accounts keys create ${KEY_FILE} \
	 --iam-account ${STORAGE_SERVICE_ACCOUNT_EMAIL}
else
	echo "using existing GCP storage SA"
fi

echo "Make sure the GCP user SA has storage admin for fulling from GCR"
  gcloud projects add-iam-policy-binding ${GOOGLE_PROJECT} --member \
	 serviceAccount:${SERVICE_ACCOUNT_EMAIL} \
	 --role=roles/storage.admin


gcloud container clusters get-credentials ${G_KF_APP} --zone $GZONE
# Upload the SA creds for storage access
kubectl create secret generic user-gcp-sa-storage \
  --from-file=user-gcp-sa.json="${KEY_FILE}"

if [ ! -d ${G_KF_APP} ]; then
  echo "No KF app, re-run fast-start.sh?"
  exit 1
  if [ ! -d ${G_KF_APP}/ks_app ]; then
    echo "ksonnet components not generated? please check."
    exit 1
  fi
fi

echo "When you are ready to connect to your Azure cluster run:"
echo "az aks get-credentials --name azure-kf-test --resource-group westus"
echo "All done!"
