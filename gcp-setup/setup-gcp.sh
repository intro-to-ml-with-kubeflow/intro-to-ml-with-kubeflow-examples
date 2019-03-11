#!/bin/bash
#tag::ubuntu[]
apt-get install google-cloud-sdk
#end::ubuntu[]
apt-get remove google-cloud-sdk
#tag::general[]
curl https://sdk.cloud.google.com | bash
#end::general[]
#tag::enable_container_apis[]
gcloud services enable container.googleapis.com
#end::enable_container_apis[]
PROJECT_ID="boos-demo-projects-are-rad"
#tag::configure_cloud_sdk[]
gcloud auth login # Launches a web browser to login with
gcloud config set project "$PROJECT_ID" #Project ID is your Google project ID
#end::configure_cloud_sdk[]
ZONE="us-central1-a" # For TPU access
CLUSTER_NAME="ci-cluster"
#tag::launch_cluster[]
gcloud beta container clusters create $CLUSTER_NAME \
       --zone $ZONE \
       --machine-type "n1-standard-4" \
       --disk-type "pd-standard" \
       --disk-size "100" \
       --scopes "https://www.googleapis.com/auth/cloud-platform" \
       --addons HorizontalPodAutoscaling,HttpLoadBalancing \
       --enable-autoupgrade \
       --enable-autorepair \
       --enable-autoscaling --min-nodes 1 --max-nodes 10 --num-nodes 2
#end::launch_cluster[]
#tag::delete_cluster[]
gcloud beta container clusters delete $CLUSTER_NAME --zone $ZONE
#end::delete_cluster[]
