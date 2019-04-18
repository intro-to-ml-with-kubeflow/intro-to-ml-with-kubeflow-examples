#!/bin/bash

multipass launch bionic -n kubeflow -m 8G -d 40G -c 4
multipass exec kubeflow -- sudo snap install microk8s --classic
multipass exec kubeflow -- microk8s.enable dns dashboard
multipass exec kubeflow -- sudo iptables -P FORWARD ACCEPT
multipass exec kubeflow -- sudo snap alias microk8s.kubectl kubectl
multipass exec kubeflow -- microk8s.enable registry
multipass exec kubeflow -- sudo snap alias microk8s.docker docker

### K8s Tools
multipass exec kubeflow -- git clone https://github.com/canonical-labs/kubernetes-tools
multipass exec kubeflow -- sudo kubernetes-tools/setup-microk8s.sh

### Kubeflow Tools
multipass exec kubeflow -- git clone https://github.com/canonical-labs/kubeflow-tools
multipass exec kubeflow -- kubeflow-tools/install-kubeflow.sh

# ### KSonnet
# multipass exec kubeflow -- wget https://github.com/ksonnet/ksonnet/releases/download/v0.13.1/ks_0.13.1_linux_amd64.tar.gz
# multipass exec kubeflow -- tar -xzf *gz
# multipass exec kubeflow -- rm *gz
# multipass exec kubeflow -- sudo cp ks*/ks /usr/local/bin

# ### Argo
# multipass exec kubeflow -- sudo curl -sSL -o /usr/local/bin/argo https://github.com/argoproj/argo/releases/download/v2.2.1/argo-linux-amd64
# multipass exec kubeflow -- sudo chmod +x /usr/local/bin/argo
# multipass exec kubeflow -- kubectl apply -f https://raw.githubusercontent.com/argoproj/argo/v2.2.1/manifests/install.yaml

### Helm and Tiller
multipass exec kubeflow -- sudo snap install helm --classic
multipass exec kubeflow -- kubectl -n kube-system create sa tiller
multipass exec kubeflow -- kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
multipass exec kubeflow -- helm init --service-account tiller
multipass exec kubeflow -- kubectl rollout status deploy/tiller-deploy -n kube-system
