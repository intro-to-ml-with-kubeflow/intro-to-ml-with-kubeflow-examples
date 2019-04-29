#!/usr/bin/env bash

set -ex

echo "Setup GCP"
./solution1.sh
source ~/.bashrc
echo "Install seldon"
./solution2.sh
echo "Optional: Set up monitoring"
./solution2b.sh
echo "Install argo"
./solution3.sh
echo "Train the model"
./solution4.sh
echo "Serve the model"
./solution5.sh
