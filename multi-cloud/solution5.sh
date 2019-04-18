#!/usr/bin/env bash

argo submit serving-sk-mnist-workflow.yaml -n kubeflow -p deploy-model=true
