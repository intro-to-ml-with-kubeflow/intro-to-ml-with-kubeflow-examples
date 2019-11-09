#!/bin/bash
if [ ! -f ~/bin/kustomize ]; then
  #tag::kustomize[]
  export KUSTOMIZE_VERSION=3.3.0
  PLATFORM=$(uname) # Either Linux or Darwin
  export PLATFORM
  mkdir -p ~/bin
  KUSTOMIZE_TAG=${KUSTOMIZE_TAG:-kustomize%2Fv$KUSTOMIZE_VERSION}
  curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/tags/${KUTOMIZE_TAG} |\
    grep browser_download |\
    grep -i "${PLATFORM}" |\
    cut -d '"' -f 4 |\
    xargs curl -O -L
  mv kustomize_*_amd64 ~/bin/kustomize
  chmod u+x ~/bin/kustomize
  # Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
  export PATH=$PATH:"~/bin"
  #end::kustomize[]
fi
