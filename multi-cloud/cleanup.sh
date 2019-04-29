#!/bin/bash

GZONE=${GZONE:="us-central1-a"} # For TPU access if we decide to go there
export G_KF_APP=${G_KF_APP:="g-kf-app"}
pushd ${G_KF_APP} && kfctl.sh delete k8s && kfctl.sh delete platform
popd
rm -rf ${G_KF_APP}
gcloud deployment-manager deployments delete ${G_KF_APP}
rm -rf ~/kf



AZURE_CLUSTER_NAME=${AZURE_CLUSTER_NAME:="azure-kf-test"}
az aks delete --name AZURE_CLUSTER_NAME

rm fast-start.sh
curl https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/fast-start.sh -o fast-start.sh
chmod a+x fast-start.sh

echo "Note: we don't cleanup the bucket right now"
