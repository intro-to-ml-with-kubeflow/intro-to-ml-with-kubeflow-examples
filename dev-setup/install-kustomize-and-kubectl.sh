#!/bin/bash
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
#tag::no-pkg-manager-kubectl[]
kubectl_release_base="https://storage.googleapis.com/kubernetes-release"
stable_url="$kubectl_release_base/release/stable.txt"
KUBECTL_VERSION=$(curl -s "$stable_url")
export KUBECTL_VERSION
curl -LO "$kubectl_release_base/$KUBECTL_VERSION/bin/$PLATFORM/amd64/kubectl"
# Now either move kubectl to /usr/bin or add it to your PATH
#end::no-pkg-manager-kubectl[]
