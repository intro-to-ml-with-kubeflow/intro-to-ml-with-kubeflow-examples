# Cross-cloud model training and serving with Kubeflow

This tutorial is designed to get you off-to-the races with cross-cloud Kubeflow.
If you don't already have a username and password for Google Cloud & Azure from the instructor gohead and get one.

## Motivation


## Set up

Kubeflow can be installed and deployed on many enivorments.
For today's tutorial we will focus on using Google & Azure.
The provided set up script is designed to be used within a Google Cloud Console instance, however you are free to modify it to run locally or do your own set-up.

### Connecting to your Google Cloud Shell

You can lunch Google Cloud Shell by clicking on the >_ icon in the top right OR by running `gcloud alpha cloud-shell ssh` if you have gcloud installed in your laptop (make sure to use the workshop account so you don't get billed).


This will give you a cloud shell, but before you dive in please enable boost mode by click on the 3 dots and selecting enable boost mode.


### Setting up your instance & clusters

While there are many ways to set up Kubeflow, in the interest of spead we will start with using a fast setup script in this directory (`fast_setup.sh`).
`fast_setup.sh` will do the following for you:

* Download Kubeflow and it dependencies
* Download Google & Azure's command line tools (if needed)
* Enable various components in 
* Set up a GKE and EKS cluster (named google-kf-test & azure-kf-test)


```bash
curl https://raw.githubusercontent.com/holdenk/intro-to-ml-with-kubeflow-examples/multi-cloud/multi-cloud/fast-start.sh -o fast-start.sh
chmod a+x fast-start.sh
./fast-start.sh
source ~/.bashrc
```

At that point it's going to be on you to start your kubeflow adventure!

### Alternatives

Note: Kubeflow's [control script](https://github.com/kubeflow/kubeflow/blob/master/scripts/kfctl.sh) also has the ability to create "platform" configuration, our fast set up script does not use this since it requires setting up an [Identity Aware Proxy](https://cloud.google.com/iap/docs/), which can add an extra 20 minutes (normally well worth, but today we're in a rush).


There is also [Kubeflow's click to deploy interface](https://deploy.kubeflow.cloud/#/deploy) (which can set up or skip IAP as desired) -- but to make this more cloud agnostic we avoided that option.

## Starting a Kubeflow project

Kubeflow provides a script to bootstrap a new kubeflow project. Kubeflow's main entry point is `kfctl.sh`, this has been added to your path with the fast-start but otherwise you can find this in the `${KUBEFLOW_SRC}/scripts/kfctl.sh`

```bash
kfctl.sh init gcp_app --platform none
cd gcp_app
kfctl.sh generate k8s
kfctl.sh apply k8s
```

Now you can see what's running in your cluster with:

```bash
kubectl get all --all-namespaces
```

### Connecting to your Kubeflow Ambdassador

The Kubeflow Ambassador gives you a nice web UI with which you can access many of Kubeflow's components.
Normally on GCP you'd set up Kubeflow in IAP mode which would give you easy access to the ambassador.

Since we're in a hurry today though we'll use port forwarding and the cloudshell web preview which is also pretty cool.

```bash
kubectl port-forward svc/ambassador -n kubeflow 8080:80
```

Now you can launch web preview and you should get the Kubeflow Ambassador page which looks something like:


