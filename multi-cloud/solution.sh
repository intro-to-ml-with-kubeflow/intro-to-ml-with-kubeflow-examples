#!/usr/bin/env bash

echo "Setup GCP"
./solution1.sh
echo "Install seldon"
./solution2.sh
echo "Install argo"
./solution3.sh
echo "Train the model"
./solution4.sh
echo "Serve the model"
./solution5.sh
