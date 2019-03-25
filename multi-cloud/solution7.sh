#!/usr/bin/env bash

# Adding hacky transporter for moving model from GCP to IBMCloud

gcloud auth configure-docker


## TODO: Download-
# 1) hacky-s3-copy/Dockerfile
# 2) hacky-s3-copy/beam-me-up-scotty.py
# 3) requirements.txt

GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null)
##
docker tag quickstart-image gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord
docker push gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord
