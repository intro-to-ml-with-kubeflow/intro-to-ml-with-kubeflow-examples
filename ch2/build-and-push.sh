#!/bin/bash
#tag::buildandpush[]
IMAGE="${CONTAINER_REGISTRY}/kubeflow/test:v1"
docker build  -t ${IMAGE} -f Dockerfile .
docker push ${IMAGE}
#end::buildandpush[]
