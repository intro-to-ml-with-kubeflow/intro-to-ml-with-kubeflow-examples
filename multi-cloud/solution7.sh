#!/usr/bin/env bash

# Adding hacky transporter for moving model from GCP to IBMCloud

gcloud auth configure-docker

wget
##
docker tag quickstart-image gcr.io/[PROJECT-ID]/quickstart-image:tag1
docker push gcr.io/[PROJECT-ID]/quickstart-image:tag1
