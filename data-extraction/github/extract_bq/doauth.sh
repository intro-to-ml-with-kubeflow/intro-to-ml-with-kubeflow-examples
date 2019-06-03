#!/bin/bash
set -ex
gcloud auth login
latest_project=$(gcloud projects list | tail -n 1 | cut -f 1  -d' ')
gcloud config set project "$latest_project"
