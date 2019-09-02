#!/bin/bash
#tag::kustomize[]
export KUSTOMIZE_VERSION=3.1.0
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
mkdir -p ~/bin
curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest |\
  grep browser_download |\
  grep -i $PLATFORM |\
  cut -d '"' -f 4 |\
  xargs curl -O -L
mv kustomize_*_amd64 ~/bin/kustomize
chmod u+x ~/bin/kustomize
# Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
export PATH=$PATH:"~/bin"
#end::kustomize[]
