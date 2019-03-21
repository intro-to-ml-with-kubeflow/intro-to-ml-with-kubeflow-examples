# Cross-cloud model training and serving with Kubeflow

This tutorial is designed to get you off-to-the races with cross-cloud Kubeflow.
If you don't already have a username and password for Google Cloud & Azure from the instructor gohead and get one.

## Motivation


## Set up

Kubeflow can be installed and deployed on many enivorments.
For today's tutorial we will focus on using Google, IBM, & Azure.
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
* Creates your first Kubeflow App with some special customizations. (See Holden for details.)

```bash
curl https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/fast-start.sh -o fast-start.sh
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
```


We want to install a few additional packages because we're going to be using
additional services. In this case `seldon-core`

```bash
#ks param set ambassador ambassadorServiceType NodePort #maybe don't need this
ks pkg install kubeflow/seldon
ks generate seldon seldon
ks apply default -c seldon
```


```
# Normally we would have done platform & k8s generate/apply as well
kfctl.sh apply k8s
```

**Possibly not needed**
Create cluster role binding.
```
kubectl create clusterrolebinding kf-admin \
     --clusterrole=cluster-admin --user=$(gcloud config get-value account)
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

## Installing Argo

Argo is a workflow management tool which we need to submit our training and serving jobs.

To download `argo` run.
```
curl -sSL -o ~/argo https://github.com/argoproj/argo/releases/download/v2.2.1/argo-linux-amd64
chmod +x ~/argo
```

To "install" `argo` :

```bash
kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.2.1/manifests/install.yaml
```

Now before you just blindly copy and paste the next part- update your NAME and EMAIL
```
kubectl create clusterrolebinding YOURNAME-cluster-admin-binding --clusterrole=cluster-admin --user=YOUREMAIL@gmail.com
```

This all seems like a _lot_ of cluster role binding... probably don't need all of these.

```
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default
kubectl create clusterrolebinding sa-admin --clusterrole=cluster-admin --serviceaccount=kubeflow:default
```

## A place for your model to call home.

A persistent volume claim.

```
kubectl create -f  -n kubeflow https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multicloud/pv-claim.yaml
```

Check to make sure it worked with

```
kubectl get pvc -n kubeflow
```

OR

console.cloud.google.com/kubernetes/storage

should look like this:

![Google Storage](./imgs/gcloud_storage.png)


## Train the Model


### Clone Example Seldon

This entire example is based loosely on https://github.com/kubeflow/example-seldon
we'll want to clone this repository to get the code and config files it uses.

```
cd ~/
git clone https://github.com/kubeflow/example-seldon
```


### Optional- Monkey with the existing model.

Some people just want to do the basics- but not you- you're  a hard charger- you
want to do all the stuff. In this little section we're going to edit the model.

The original model that is being trained is a `RandomForrestClassifier` which is
a pretty trashy way to categorize handwritten digits.

Luckily `sklearn` has a nice consistent API so we can swap out about any classifier in its place.

To do this, in the place where you cloned `example-seldon` let's go edit the training file.

Goto `example-seldon/models/sk_mnist/train`.  Check the file `create_model.py`.

The lines of interest are 39 through 42
```
classifier = RandomForestClassifier(n_estimators=30)

classifier.fit(data[:n_samples // 2], targets[:n_samples // 2])
```

Thanks to the magic of python- you don't even need to change the second line.

You'll need to import your new classifier (up towards the begining), and here on line 39
declare classifier as what ever new and better one you want.

While you're in here, please take a look at various things like the rest of `create_model.py`, `Dockerfile`, and `build_and_push.sh`.

These are all interesting things, but going in to the finer details of creating a workflow is a bit out of scope, and we feel you can figure
it out pretty easily on your own once this is done.


### Ok Now train it.

IF you didn't monkey with the model:
```bash
cd $EXAMPE_SELDON
argo submit training-sk-mnist-workflow.yaml -n kubeflow
```

ELSE IF you monkeyed with the model, you'll need to train and build a new image:

```bash
cd $EXAMPE_SELDON
argo submit training-sk-mnist-workflow.yaml -n kubeflow -p build-push-image=true
```

Which will build and push the new docker image as part of the work flow. This workflow
has a `build-push-image` parameter that will reload the image. You can check that out [here](

### Ok now monitor it.

The easiest way to monitor the model progress is using the following two shell commands:

```
kubectl get pods -n kubeflow | grep sk-train
## AND
argo list -n kubeflow
```

These will hopefully show a successfully running set of pods / job.

## Serve the Model

Once training has finished, we can serve it with:

```
cd $EXAMPLE_SELDON/workflows
argo submit serving-sk-mnist-workflow.yaml -n kubeflow -p deploy-model=true
```

Now talk about monitoring and querying

