#!/bin/bash
if [ ! -f ~/bin/kustomize ]; then
  #tag::kustomize[]
  PLATFORM=$(uname) # Either Linux or Darwin
  export PLATFORM
  mkdir -p ~/bin
  KVERSION=${KVERSION:-3.3.0}
  # The same project releases multiple kinds of artifacts
  KUSTOMIZE_TAG=${KUSTOMIZE_TAG:-kustomize%2Fv$KVERSION}
  curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/tags/${KUSTOMIZE_TAG} |\
    grep browser_download |\
    grep -i "${PLATFORM}" |\
    cut -d '"' -f 4 |\
    xargs curl -O -L
  tar -xvf kustomize_*${KVERSION}*.tar.gz
  mv kustomize ~/bin/kustomize
  chmod u+x ~/bin/kustomize
  # Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
  export PATH=$PATH:"~/bin"
  #end::kustomize[]
fi
