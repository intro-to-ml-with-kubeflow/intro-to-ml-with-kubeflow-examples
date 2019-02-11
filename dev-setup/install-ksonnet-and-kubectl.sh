#!/bin/bash
#tag::ksonnet[]
export KSONNET_VERSION=0.11.0
export PLATFORM=$(uname) # Either Linux or Darwin
curl -OL https://github.com/ksonnet/ksonnet/releases/download/v$KSONNET_VERSION/ks_$KSONNET_VERSION_$PLATFORM_amd64.tar.gz
tar zxf ks_$KSONNET_VERSION_$PLATFORM_amd64.tar.gz
# Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
export PATH=$PATH:$(pwd)/ks_0.11.0_$PLATFORM_amd64
#end::ksonnet[]
#tag::ubuntu-kubectl[]
sudo snap install kubectl --classic
#end::ubuntu-kubectl[]
#tag::debian-kubectl[]
sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
#end::debian-kubectl[]
#tag::redhat-kubectl[]
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
yum install -y kubectl
#end::redhat-kubectl[]
#tag::osx-kubectl[]
brew install kubernetes-cli
#end::osx-kubectl[]
#begin::no-pkg-manager-kubectl[]
export KUBECTL_VERSION=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)
curl -LO https://storage.googleapis.com/kubernetes-release/release/$KUBECTL_VERSION/bin/$PLATFORM/amd64/kubectl
# Now either move kubectl to /usr/bin or add it to your PATH
#end::no-pkg-manager-kubectl[]
