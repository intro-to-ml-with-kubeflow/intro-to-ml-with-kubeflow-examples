#!/bin/bash

#tag::build[]
docker build . -t kf-steps/bq-extract:v8
#end::build[]
# We also have a docker compose file
docker-compose build
#tag::manualrun[]
docker run -ti --name gcloud-config --entrypoint "/doauth.sh" kf-steps/bq-extract:v2
docker run --volumes-from gcloud-config google/cloud-sdk
#end::manualrun[]
#tag::push[]
docker tag kf-steps/bq-extract:v8 gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v8
docker push gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v8
#end::push[]
#tag::run[]
cd default
kustomize edit add configmap github-data-extract --from-literal=projectName=${PROJECT_NAME}
kustomize build . | kubectl apply -f -
#end::run[]
#tag::verify[]
kubectl get jobs |grep gh-data
#end::verify[]
