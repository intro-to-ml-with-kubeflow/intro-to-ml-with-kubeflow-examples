GZONE=${GZONE:="us-central1-a"} # For TPU access if we decide to go there
GOOGLE_CLUSTER_NAME=${GOOGLE_CLUSTER_NAME:="google-kf-test"}

gcloud beta container clusters delete $GOOGLE_CLUSTER_NAME -- zone $GZONE
AZURE_CLUSTER_NAME=${GOOGLE_CLUSTER_NAME:="azure-kf-test"}
az aks delete --name AZURE_CLUSTER_NAME
