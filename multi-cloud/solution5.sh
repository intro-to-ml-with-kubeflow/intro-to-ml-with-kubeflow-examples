#!/usr/bin/env bash

cd ~/example-seldon/workflows
argo submit serving-sk-mnist-workflow.yaml -n kubeflow -p deploy-model=true
