#!/bin/bash

set -ex
# Hi friends! I'm the solution guide. If you get stuck I'm here to help
# Some other places you might want to look for help first:
# 1) 

kfctl.sh init gcp_app --platform none
cd gcp_app
kfctl.sh generate k8s
kfctl.sh apply k8s

