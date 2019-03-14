# Cross-cloud model training and serving with Kubeflow

This tutorial is designed to get you off-to-the races with cross-cloud Kubeflow.
If you don't already have a username and password for Google Cloud & Azure from the instructor gohead and get one.

## Motivation


## Set up

Kubeflow can be installed and deployed on many enivorments.
For today's tutorial we will focus on using Google & Azure.
The provided set up script is designed to be used within a Google Cloud Console instance, however you are free to modify it to run locally.


While there are many ways to set up Kubeflow, in the interest of spead we will start with using a fast setup script in this directory (`fast_setup.sh`).
`fast_setup.sh` will do the following for you:

* Download Kubeflow and it dependencies
* Download Google & Azure's command line tools (if needed)
* Enable various components in 
* Set up a GKE and EKS cluster (named google-kf-test & azure-kf-test)

At that point it's going to be on you to start your kubeflow adventure!

## Starting a Kubeflow project

Kubeflow provides a script to bootstrap a new kubeflow project
