#!/usr/bin/env bash

set -ex

echo "Setup GCP"
source solution1.sh
source ~/.bashrc
echo "Install seldon"
source solution2.sh
echo "Optional: Set up monitoring"
source solution2b.sh
echo "Install argo"
source solution3.sh
echo "Train the model"
source solution4.sh
echo "Serve the model"
source solution5.sh
echo "Uploading the model to S3 so we can access it from IBM"
source solution7.sh
