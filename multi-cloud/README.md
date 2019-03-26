# Cross-cloud model training and serving with Kubeflow

This tutorial is designed to get you off-to-the races with cross-cloud Kubeflow.
If you don't already have a username and password for Google Cloud & Azure from the instructor go head and get one.

**Note:** If you're looking at this and the images are broken [click here](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/README.md)


**Note:** If you find bugs, or have suggestions please consider e-mailing us, or submitting a PR if you know how to fix or improve it. There is also a shared [note's document](https://docs.google.com/document/d/1V6Q8z-BiaFCvdBaLg1n3BDTZpXsNroN24YFHXH7Ri68/edit?usp=sharing) that you are more than welcome to contribute to (and we can get you some coffee or SWAG as thanks)

**Note:** There is no need to make a GKE cluster manually before starting this tutorial, we will configure one as we go along.

## Motivation

We've picked a relatively un-complicated machine learning example, the data is already prepared, so that you can focus on exploring Kubeflow and how to deploy Kubeflow on multiple clouds.


We also train a default model so you don't get hung up on that, but it isn't a very good model for the problem, so if you've got time and want to explore more you can jump in there.



## For when thing's go wrong

Hopefully it hasn't broken for you, but in case something goes wrong feel free to come up here and take a look.

#### Solution guide

If at any point you get lost, that's totally normal. Feel free to look at the fancy (we use bash!) [solution shell scripts https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/tree/master/multi-cloud](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/tree/master/multi-cloud).


#### Debugging

There are a few different tools for debugging what's going wrong.
The `kubectl` program gives you a way to get the description of a pod which can include useful error information.

```bash
kubectl describe pod -n kubeflow [podname]
```

The logs of the pod also often contain useful information:

```bash
kubectl logs -n kubeflow [podname]
```


In Kubeflow it's common for there to be multiple containers, so you may need to add `-c main` (or similar) to get the logs.

#### If you want to start over

**Note:*** If you get into a really bad state there is also a cleanup script you may find useful.
Manually deleting the Kubernetes cluster can leave you in a weird state, since the GCP deployment has a number of ancillary services deployed along side.
The [cleanup script is at https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/cleanup.sh](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/cleanup.sh).

```bash
curl https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/cleanup.sh -o cleanup.sh
chmod a+x cleanup.sh
./cleanup.sh
source ~/.bashrc
```

## Set up

Kubeflow can be installed and deployed on many environments.
For today's tutorial we will focus on using Google, IBM, & Azure.
The provided set up script is designed to be used within a Google Cloud Console instance, however you are free to modify it to run locally or do your own set-up.

### Logging in to cloud console

If you already have a gcloud account you may find it easier to use incognito mode. You can log in to the cloud console by going to https://console.cloud.google.com.
Once you're in the default project should already be selected, but if not you can select it by clicking on the project drop down in the top left

![Project drop down location](./imgs/select_project_left_top.png)

Then selecting the project. Everyone may have a different project name, don't worry about this.
![Select project](./imgs/select_project_picker.png)

### Connecting to your Google Cloud Shell

You can lunch Google Cloud Shell by clicking on the >_ icon in the top right if you have gcloud installed in your laptop (make sure to use the workshop account so you don't get billed).

![Cloud shell launch](./imgs/cloud-console-button.png)

Note: there is a gcloud alpha ssh command, but we'll be use the webpreview which doesn't work out of the box with this.


This will give you a cloud shell, but before you dive in please enable boost mode by click on the 3 dots and selecting enable boost mode.

![The 3 dots to click on to get the advanced menu](./imgs/area_to_enable_boost.png)

![Advanced menue expanded](./imgs/enable-boost-expanded.png)

#### Optional: Using screen

Since conference WiFi is unpredictable, you may wish to use [screen](https://www.rackaid.com/blog/linux-screen-tutorial-and-how-to/).
This will allow you to re-connect your terminal session in another connection

### Setting up your instance & clusters

While there are many ways to set up Kubeflow, in the interest of speed we will start with using a fast setup script in this directory (`fast_setup.sh`).
`fast_setup.sh` will do the following for you:

* Download Kubeflow and it dependencies
* Download Google & Azure's command line tools (if needed)
* Enable various components in
* Set up a GKE and EKS cluster (named google-kf-test & azure-kf-test)
* Creates your first Kubeflow App on GKE with some special customizations to avoid waiting for certificate provissioning

If you wish to skip building an Azure cluster you can set: `SKIP_AZURE=1` as an environmental variable to the below script.

```bash
curl https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/fast-start.sh -o fast-start.sh
chmod a+x fast-start.sh
./fast-start.sh 2>&1 | tee startup-logs
echo $?
source ~/.bashrc
```

At that point it's going to be on you to start your Kubeflow adventure!

**Note:** Look up to see how to cleanup, in case you run into problems. tl;dr The [cleanup script is at https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/cleanup.sh](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/cleanup.sh).

#### Alternatives

There is also [Kubeflow's click to deploy interface](https://deploy.kubeflow.cloud/#/deploy) (which can set up or skip IAP as desired) -- but to make this more cloud agnostic we avoided that option.


In addition to generating K8s configurations, Kubeflow also has the tools (for some platforms) to generate all of the ancillary configuration (enabling services, creating a K8s cluster, etc.).


`fast-start.sh` takes advantage of  `kfctl.sh` GCP platform generation and manually disables IAP mode.
For now the Azure resources are created manually inside of fast-start, but Azure has been added as a supported platform to `kfctl` in the master branch of Kubeflow.

### Loading your Kubeflow application

To support disabling IAP mode we've generated your GCP Kubeflow app and made some non-standard configuration changes.
To hide all our dirty laundry, we've done this by starting a Kubeflow application for you and setting some hidden parameters (you can look inside of fast-start.sh if you're curious).
To load your application and apply Kubeflow's Kubernetes configuration you run:


```bash
pushd g-kf-app
source env.sh
```

Kubeflow's main entry point is `kfctl.sh`, this has been added to your path with the fast-start but otherwise you can find this in the `${KUBEFLOW_SRC}/scripts/kfctl.sh`.
Now that you have your application loaded and a kubernetes cluster created, it's time to apply Kubeflow's kubernetes configuration:

```bash
kfctl.sh apply k8s
```


*Note*: This will take awhile, however if you're stuck waiting for the ambassador to deploy, double check that your cloudshell is running in boost mode. If it's not you may want to restart in boost mode, although you'll need to delete the deployment in deployment manager and start over, but trust us this is the best time to start over rather than 2 hours later.

Now you can see what's running in your cluster with:

```bash
kubectl get all --all-namespaces
```

You should see a variety of things deployed including the ambassador in the Kubeflow namespace e.g.:

```
kubeflow             deployment.apps/ambassador                                 3         3         3            3           19h
```

### Connecting to your Kubeflow Ambassador

The Kubeflow Ambassador gives you a nice web UI with which you can access many of Kubeflow's components.
Normally on GCP you'd set up Kubeflow in IAP mode which would give you easy access to the ambassador.

Since we're in a hurry today though we'll use port forwarding and the cloudshell web preview which is also pretty cool.

```bash
kubectl port-forward svc/ambassador -n kubeflow 8080:80 &
```

The cloudshell web preview button looks like and should be at the top of your cloudshell web interface

![image of cloudshell webpreview button](./imgs/web_preview.png)

The default port should be 8080 which is the correct one, but you change it if not:

![image of cloudhsell port selection](./imgs/webpreview_w_port.png)

Now you can launch web preview and you should get the Kubeflow Ambassador page which looks something like:

![Image of Ambassador Web UI](./imgs/kf_ambassador.png)




### Adding components to your Kubeflow application


We want to install a few additional packages because we're going to be using
additional services.
Currently Kubeflow manages packages with [ksonnet](https://ksonnet.io/), although [this is changing](https://groups.google.com/forum/#!searchin/kubeflow-discuss/ksonnet%7Csort:date/kubeflow-discuss/Zg14_Ok7XH4/iL7bHZo6CgAJ).
`kfctl.sh` creates a ksonnet application inside of your kubeflow application called `ks_app`.
Ksonnet Packages which are shipped with kubeflow can be installed by going into the `ks_app` directory with and running `ks pkg install kubeflow/[package_name]`.


Our example uses [seldon core](https://www.seldon.io/) for model serving, called `seldon` inside of Kubeflow.


Once inside the `ks_app` directory, you can make sure it's installed by running `ks pkg list` and looking for `*` next to seldon:

```
programmerboo@cloudshell:~/g-kf-app-4/ks_app (workshop-test-234519)$ ks pkg list
REGISTRY NAME                    INSTALLED
======== ====                    =========
kubeflow application             *
kubeflow argo                    *
kubeflow automation
kubeflow chainer-job
kubeflow common                  *
kubeflow examples                *
kubeflow gcp                     *
kubeflow jupyter                 *
kubeflow katib                   *
kubeflow kubebench
kubeflow metacontroller          *
kubeflow modeldb                 *
kubeflow mpi-job                 *
kubeflow mxnet-job
kubeflow new-package-stub
kubeflow nvidia-inference-server
kubeflow openmpi
kubeflow openvino                *
kubeflow pachyderm
kubeflow pipeline                *
kubeflow profiles                *
kubeflow pytorch-job             *
kubeflow seldon                  *
kubeflow tensorboard
kubeflow tf-batch-predict
kubeflow tf-serving              *
kubeflow tf-training             *
```

If it is not installed (although the default path should install it), go ahead and install it now.
You can also try installing the `pachyderm` package, which can be useful later.

If this doesn't work for you, remember we have the [solutions](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/blob/master/multi-cloud/solution2.sh) in the [repo](https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/tree/master/multi-cloud).

Once you've installed your new component you have the opportunity to configure it with:

```bash
ks param set [component_name] [config_key] [value]
```

For now, we don't need to configure anything inside of seldon, so we can use the default configuration.


If you change the configuration of a component (or if it's the first time installing it), you need to regenerate the yaml files for that component. This is done `ks generate`. We'll do this using the seldon prototype and seldon component:

```bash
ks generate [prototype] [component]
```

You can verify the components with:

```bash
ks component list
```


Now we can use `kfctl.sh` to apply our newly generated yaml. Make sure to run this in the root of your kubeflow project.

```
cd ..
kfctl.sh apply k8s
```


Now you can see what's running in your cluster with:

```bash
kubectl get all --all-namespaces
```

#### Optional: Adding Helm/Tiller for seldon monitoring

We don't require it for our example, but seldon has some additional monitoring tools you can install using helm/tiller.

#### Optional: Adding vendor/external components to your Kubeflow application

If you want to add packages which aren't part of the Kubeflow core,
you can add additional registries with `ks registry add`.
For example adding the h2o registry could be done with:

```bash
ks registry add h2o-kubeflow https://github.com/h2oai/h2o-kubeflow/tree/master/h2o-kubeflow
```

Now that you've add a new registry you can list the components and install them in the same way as with first party components up above.

### Setting up the requirements to train a simple model

#### Installing Argo

Argo is a workflow management tool, and serves as the basis of Kubeflow pipelines.
Currently, Kubeflow pipelines depend on some GCP specific components, so we will instead use Argo directly (this should be fixed eventually).

To download `argo` run.
```
curl -sSL -o ~/argo https://github.com/argoproj/argo/releases/download/v2.2.1/argo-linux-amd64
chmod +x ~/argo
```

Then we want to give the Kubeflow default service account permission to run everything it needs in the workflow:

```bash
kubectl create clusterrolebinding sa-admin --clusterrole=cluster-admin --serviceaccount=kubeflow:default
```

#### A place for your model to call home.

A persistent volume claim provides a way to store data with a lifecycle independent of the pod.
We'll use the persistent volume as a place to store the model during training, and then read it back for serving in a different pod.

```
kubectl create -f https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml -n kubeflow
```

Check to make sure it worked with

```
kubectl get pvc -n kubeflow
```

OR

https://console.cloud.google.com/kubernetes/storage

should look like this:

![Google Storage](./imgs/gcloud_storage.png)


### Train the Model


#### Clone Example Seldon

This entire example is based loosely on https://github.com/kubeflow/example-seldon
we'll want to clone this repository to get the code and config files it uses.

```
cd ~/
git clone https://github.com/kubeflow/example-seldon
```


#### Optional- Monkey with the existing model.

Some people just want to do the basics- but not you- you're  a hard charger- you
want to do all the stuff. In this little section we're going to edit the model.

The original model that is being trained is a `RandomForrestClassifier` which is
a pretty trashy way to categorize handwritten digits.

Luckily `sklearn` has a nice consistent API so we can swap out about any classifier in its place.

To do this, in the place where you cloned `example-seldon` let's go edit the training file.

Go to `example-seldon/models/sk_mnist/train`.  Check the file `create_model.py`.

The lines of interest are 39 through 42
```
classifier = RandomForestClassifier(n_estimators=30)

classifier.fit(data[:n_samples // 2], targets[:n_samples // 2])
```

Thanks to the magic of python- you don't even need to change the second line.

You'll need to import your new classifier (up towards the beginning), and here on line 39
declare classifier as what ever new and better one you want.

While you're in here, please take a look at various things like the rest of `create_model.py`, `Dockerfile`, and `build_and_push.sh`.

These are all interesting things, but going in to the finer details of creating a workflow is a bit out of scope, and we feel you can figure
it out pretty easily on your own once this is done.


### Ok Now train it.

IF you didn't monkey with the model:
```bash
export EXAMPLE_SELDON=~/example-seldon
cd $EXAMPLE_SELDON/workflows
~/argo submit training-sk-mnist-workflow.yaml -n kubeflow
```

ELSE IF you monkeyed with the model, you'll need to train and build a new image.

Building a new image requires configuring your own Docker credentials so that it can be pushed.
The example workflow is expecting you to supply a Kubernetes Secret with the following values:

```yml
apiVersion: v1
data:
  password: <YOUR_PASSWORD_BASE64>
  username: <YOUR_USERNAME_BASE64>
kind: Secret
metadata:
  name: docker-credentials
  namespace: kubeflow
type: Opaque
```

Once you define such a secret, run `kubectl apply -f secret.yml` to apply it to the `kubeflow` namespace, before running the below commands.

```bash
export EXAMPLE_SELDON=~/example-seldon
cd $EXAMPLE_SELDON/workflows
~/argo submit training-sk-mnist-workflow.yaml -n kubeflow -p build-push-image=true
```

Which will build and push the new docker image as part of the work flow. This workflow
has a `build-push-image` parameter that will reload the image. You can check that out [here]().

### Ok now monitor it.

The easiest way to monitor the model progress is using the following two shell commands:

```
kubectl get pods -n kubeflow -w | grep sk-train
## AND
~/argo list -n kubeflow
```

These will hopefully show a successfully running set of pods / job.

You should follow along as the Pod goes from `Pending` --> `ContainerCreating` --> `Running` --> `Completed` using the get kubectl pods command.

In addition, you can use the `~/argo get [WORKFLOW_NAME] -n kubeflow`, `~/argo list [WORKFLOW_NAME] -n kubeflow`, `~/argo describe [WORKFLOW_NAME] -n kubeflow`, and `~/argo delete [WORKFLOW_NAME] -n kubeflow` to interact with workflows that you create.

### Serve the Model

Once training has finished, we can serve it with:

```
cd $EXAMPLE_SELDON/workflows
~/argo submit serving-sk-mnist-workflow.yaml -n kubeflow  -p deploy-model=true
```

To query the service: you will firstly grab one of the service endpoints by running `kubectl describe svc ambassador -n kubeflow | grep Endpoints`, which grabs the endpoints of the running ambassador deployment. Next you will run `~/argo list -n kubeflow | grep seldon-sk-deploy` to grab the successful deployment name. Now you can curl by hitting the REST endpoint:
```bash
# The version should be v0.1 to start
http://<ambassadorEndpoint>/seldon/<deploymentName>/api/<version>/predictions
```

You may also port-forward the ambassador service for a better dev experience.

#### Getting the model ready for serving on another cloud

This workflow saves the model results to a persistent-volume-claim, however we can't move this between clouds.
To support this we will configure using GCS or another [S3 compatable backend credintals as in the IBM guide](https://github.com/intro-to-ml-with-kubeflow/ibm-install-guide/blob/master/once-cluster-is-up.sh).


Tensorflow has the ability to write to object stores, and the [tfjob operator component has been improved to make this easier](https://github.com/kubeflow/examples/pull/499/files) (however it's not in the current release)
using secrets for managing the object store credentials.


For now, and since we're using sklearn anyways, we'll use a special version of this code Trevor.


**Note:** This is not great practice, longer term you'll want to use something like the update tfjob operator or otherwise store and fetch credentials rather than putting them in source.


#### Query the Model

#### Monitor the serving

If you set up the optional seldon analytics...

### Optional: s/sklearn/tensorflow/

A non-zero percentage of you probably came here looking for Tensorflow on Kubernetes, and random forest isn't all that good for mnist anyways.
Now we train a Tensorflow model really quickly:

```bash
argo submit training-tf-mnist-workflow.yaml -n kubeflow
```

And party on*


## Starting a new Kubeflow project for Azure/IBM

Now that we've got everything working on GCP, it's time to take our model and serve it on another cloud provider.

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

### Getting your model ready

If you're running short on time, feel free to skip re-training your model and instead copy your model over.

#### Optional: re-training



#### Optional: copy your model.


### Serving

## Next steps and other resources

We hope this has been useful to you and increased your interest in learning more about Kubeflow.
The Kubeflow project [has a collection of examples on GitHub](https://github.com/kubeflow/examples).
There is also a [discussion list](https://groups.google.com/forum/#!forum/kubeflow-discuss) and [the Kubeflow slack](http://kubeflow.slack.com) [and invite link](https://kubeflow.slack.com/join/shared_invite/enQtNDg5MTM4NTQyNjczLWUyZGI1ZmExZWExYWY4YzlkOWI4NjljNjJhZjhjMjEwNGFjNmVkNjg2NTg4M2I0ZTM5NDExZWI5YTIyMzVmNzM) for your questions.


Boris @ LightBend has written a series of blog posts on how to use [Kubeflow With OpenShift](https://www.lightbend.com/blog/how-to-deploy-kubeflow-on-lightbend-platform-openshift-kubeflow-tensorflow-jobs).


Some of us are also working on [a book about Kubeflow, and you can join the mailing list to find out more](http://www.introductiontomlwithkubeflow.com/).

#### Let's go cross cloud!

OK- read this to get your IBM cloud set up (just need gui, no cloud cli tools)
https://console.bluemix.net/docs/services/cloud-object-storage/basics/order-storage.html#order-storage

Create a Cloud Object Storage Service

Create credentials.

When you create the creds, you click on the little triange to expand them, then look at this- and figure it out.

see this https://console.bluemix.net/docs/services/cloud-object-storage/libraries/python.html#using-python

