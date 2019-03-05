#!/bin/bash
#tag::installmicrok8s[]
sudo snap install microk8s --classic
#end::installmicrok8s[]
#tag::setupmicrok8s[]
# Alias the microk8s versions of kubectl and docker so kubeflow uses them
# You will want to add this to your bashrc if you intend to use microk8s
# generally.
alias kubectl="microk8s.kubectl"
alias docker="microk8s.docker"
### Faking Docker registry, skip for production docker registry
microk8s.enable registry
export DOCKER_HOST="unix:///var/snap/microk8s/current/docker.sock"
sudo ln -s /var/snap/microk8s/current/docker.sock /var/run/docker.sock
sudo ln -s /var/snap/microk8s/common/var/lib/docker /var/lib/docker
#end::setupmicrok8s[]
#tag::bootstrapwithcanonicallabs[]
git clone https://github.com/canonical-labs/kubeflow-tools
pushd kubeflow-tools
KUBEFLOW_VERSION=0.4.1 ./install-kubeflow.sh
#end::bootstrapwithcanonicallabs[]
#tag::unaliasmicrok8s[]
unalias kubectl
unalias docker
#end::unaliasmicrok8s[]
