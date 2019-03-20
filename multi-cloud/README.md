# Cross-cloud model training and serving with Kubeflow

This tutorial is designed to get you off-to-the races with cross-cloud Kubeflow.
If you don't already have a username and password for Google Cloud & Azure from the instructor gohead and get one.

## Motivation


## Set up

Kubeflow can be installed and deployed on many enivorments.
For today's tutorial we will focus on using Google & Azure.
The provided set up script is designed to be used within a Google Cloud Console instance, however you are free to modify it to run locally or do your own set-up.

### Logging in to cloud console

If you already have a gcloud account you may find it easier to use incognito mode. You can log in to the cloud console by going to https://console.cloud.google.com . 
Once you're in the default project should already be selected but if not you can select it by clicking on the project drop down in the top left

![Project drop down location](./imgs/select_project_left_top.png)

Then selecting the project. Everyone may have a different project name, don't worry about this.
![Select project](./imgs/select_project_picker.png)

### Connecting to your Google Cloud Shell

You can lunch Google Cloud Shell by clicking on the >_ icon in the top right if you have gcloud installed in your laptop (make sure to use the workshop account so you don't get billed).
![Cloud shell launch](cloud-console-button.png)

Note: there is a gcloud alpha ssh command, but we'll be use the webpreview which doesn't work out of the box with this.


This will give you a cloud shell, but before you dive in please enable boost mode by click on the 3 dots and selecting enable boost mode.
![The 3 dots to click on to get the advanced menu](area_to_enable_boost.png)

![Advanced menue expanded](enable-boost-expanded.png)

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

There is also [Kubeflow's click to deploy interface](https://deploy.kubeflow.cloud/#/deploy) (which can set up or skip IAP as desired) -- but to make this more cloud agnostic we avoided that option.


In addition to generating K8s configurations, Kubeflow also has the tools (for some platforms) to generate all of the ancilary configuration (enabling services, creating a K8s cluster, etc.).


`fast-start.sh` takes advantage of  `kfctl.sh` GCP platform generation and manually disables IAP mode.
For now the Azure resources are created manually inside of fast-start, but Azure has been added as a supported platform to `kfctl` in the master branch of Kubeflow.

### Loading your Kubeflow application

To support disabling IAP mode we've generated your GCP kubeflow app and made some non-standard configuration changes.
To loud your application and apply Kubeflow's Kubernetes configuration you run:

Kubeflow's main entry point is `kfctl.sh`, this has been added to your path with the fast-start but otherwise you can find this in the `${KUBEFLOW_SRC}/scripts/kfctl.sh`.


```bash
pushd g-kf-app
source env.sh
# Normally we would have done platform & k8s generate/apply as well
kfctl.sh apply k8s
```

Now you can see what's running in your cluster with:

```bash
kubectl get all --all-namespaces
```



### Connecting to your Kubeflow Ambassador

The Kubeflow Ambassador gives you a nice web UI with which you can access many of Kubeflow's components.
Normally on GCP you'd set up Kubeflow in IAP mode which would give you easy access to the ambassador.

Since we're in a hurry today though we'll use port forwarding and the cloudshell web preview which is also pretty cool.

```bash
kubectl port-forward svc/ambassador -n kubeflow 8080:80 &
```

The cloudshell web preview button looks like and should be at the top of your cloudhsell web interface

![image of cloudshell webpreview button](./imgs/web_preview.png)

The default port should be 8080 which is the correct one, but you change it if not:

![image of cloudhsell port selection](./imgs/webpreview_w_port.png)

Now you can launch web preview and you should get the Kubeflow Ambassador page which looks something like:

![Image of Ambassador Web UI](./imgs/kf_ambassador.png)



## Starting a new Kubeflow project for Azure

First we'll connect to our Azure cluster:

```bash
az aks get-credentials --name azure-kf-test --resource-group westus
```

Since Azure platform isn't supported in 0.4.1  we'll instead use it as a "raw" k8s cluster.
Kubeflow provides `kfctl.sh` is also used to bootstrap a new kubeflow project:


```bash
kfctl.sh init azure-app --platform none
cd azure-app
kfctl.sh generate k8s
kfctl.sh apply k8s
```

Now you can see what's running in your cluster with:

```bash
kubectl get all --all-namespaces
```
