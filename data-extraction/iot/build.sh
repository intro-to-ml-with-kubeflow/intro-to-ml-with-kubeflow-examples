#!/bin/bash

CONTAINER_REGISTRY="gcr.io/${PROJECT_NAME}"
#tag::buildandpush[]
TARGET="${CONTAINER_REGISTRY}/kf-steps/iot-extract:v2"
docker build . -t "${TARGET}"
docker push "${TARGET}"
#end::buildandpush[]
#tag::run[]
kubectl apply -f iot_extract_job.yaml
#end::run[]
#tag::verify[]
kubectl get jobs |grep gh-data
#end::verify[]
