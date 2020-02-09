#!/bin/bash
#tag::deploy[]
#Configuration
export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v0.7-branch/kfdef/kfctl_k8s_istio.0.7.1.yaml"
# ${KF_DIR} is the name for the kubeflow deployment
mkdir -p ${KF_DIR}
cd ${KF_DIR}
kfctl apply -V -f ${CONFIG_URI}
#end::deploy[]
