#!/bin/bash
#tag::kustomize[]
PLATFORM=$(uname) # Either Linux or Darwin
export PLATFORM
mkdir -p ~/bin
KUSTOMIZE_URL=$(curl -s https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest |\
  grep browser_download |\
  grep -i "${PLATFORM}" |\
  cut -d '"' -f 4)
wget "${KUSTOMIZE_URL}"
KUSTOMIZE_FILE=${KUSTOMIZE_URL##*/}
tar -xvf "${KUSTOMIZE_FILE}"
rm "${KUSTOMIZE_FILE}"
mv kustomize ~/bin/kustomize
chmod u+x ~/bin/kustomize
# Add this + platform/version exports to your bashrc or move the ks bin into /usr/bin
export PATH=$PATH:"~/bin"
#end::kustomize[]
