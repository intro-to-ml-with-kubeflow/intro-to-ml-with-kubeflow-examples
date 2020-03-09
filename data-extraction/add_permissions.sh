#!/bin/bash
# Add permissions to the notebook service account
USER_NAMESPACE=${USER_NAMESPACE:-"programmerboo"}
NOTEBOOK_SERVICE_ACCOUNT=${NOTEBOOK_SERVICE_ACCOUNT:-"${USER_NAMESPACE}:default-editor"}
kubectl create rolebinding spark-role-${USER_NAMESPACE} --role=edit --serviceaccount=${NOTEBOOK_SERVICE_ACCOUNT} --namespace=${USER_NAMESPACE}
