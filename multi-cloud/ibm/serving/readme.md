

### Step 1: Create Bluemix Acct

#### Web Create acct

#### Install Cli

See console.bluemix.net/docs/cli/reference/ibmcloud/download_cli.html

```bash
wget https://public.dhe.ibm.com/cloud/bluemix/cli/bluemix-cli/0.14.0/IBM_Cloud_CLI_0.14.0_amd64.tar.gz
tar -zxf IBM_Cloud_CLI_0.14.0_amd64.tar.gz
cd Bluemix_CLI
./install
```

Now you can login with
```bash
ibmcloud login
ibmcloud plugin install container-service
ibmcloud plugin install container-registry #for docker
```


### Step 2: Create Cloud Storage Service

OK- read this to get your IBM cloud set up (just need GUI, no cloud-cli tools)
https://console.bluemix.net/docs/services/cloud-object-storage/basics/order-storage.html#order-storage

There is a video on how to do this at https://www.youtube.com/watch?v=GO2ODP5p3po&feature=youtu.be

### Step 3: Push Model from GCP to your Cloud Storage

Now you've got the credentials you need! It's time to go ahead and clone our repo and get do a kind of hacky copy into S3.

```bash
cd ~/
git clone https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples.git
export WORKSHOP_HOME=~/intro-to-ml-with-kubeflow-examples.git
pushd $WORKSHOP_HOME/multi-cloud/hacky-s3-copy
```


Look inside of the `beam-me-up-scotty.py` script and hard code your credentials.

**Note:** Normally you'd use secrets, but since this is going to be deprecated anyways we'll just hard code it.

Now you can build and push this image, we have a template to run it called hacky-s3-copy.yaml that expects it to be at `gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord`.
If you get lost `solution7.sh` will show you how.


### Step 4: Create K8s cluster on IBM

**Note:** We have some pre-baked IBM K8s clusters you can have, come talk to us!

Log in to Bluemix-

1. Click on Hamburger in top right.
2. Click Kubernetes.
3. Click on "Create Cluster"
4. Name it "ibm-serving-demo"

Follow directions on next page in GCP cloud shell.

Probably something like

```bash
ibmcloud ks region-set us-south
ibmcloud ks cluster-config ibm-serving-demo
```
^^ That will throw an error until the cluster is up- check status with

```bash
ibmcloud ks clusters
```

Should only take 20-30 minutes or so-


```bash
ibmcloud ks cluster-config ibm-serving-demo
```

That's going to give you a command to run:

```bash
export KUBECONFIG=/home/$USER/.bluemix/plugins/container-service/clusters/ibm-serving-demo/kube-config-hou02-ibm-serving-demo.yml
```

### Step 5: Install Seldon Core

#### Install seldon-core

Init Serving App
```bash
cd ~/
ks init ibm-serving-app --api-spec=version:v1.8.0
```

```bash
cd ibm-serving-app
ks registry add seldon-core github.com/SeldonIO/seldon-core/tree/master/seldon-core
ks pkg install seldon-core/seldon-core@master
ks generate seldon-core seldon-core

kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo/v2.2.1/manifests/install.yaml
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=default:default

```


Apply everything

```
ks apply default
```


#### Download image serving files

```bash
cd ~/
mkdir ibm-serving
cd ibm-serving
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/contract.json
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/requirements.txt
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/SkMnist.py
mkdir .s2i
cd .s2i
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/.s2i/environment
cd ..
```

#### Install s2i

s2i is a program that creates images out of source files.

```bash
wget https://github.com/openshift/source-to-image/releases/download/v1.1.13/source-to-image-v1.1.13-b54d75d3-linux-amd64.tar.gz
tar -xvf source-to-image-v1.1.13-b54d75d3-linux-amd64.tar.gz
```


### Building Image

### Step 3.1: Setup Container Registry on IBM side

```
NAMESPACE=serving-demo
ibmcloud cr namespace-add $NAMESPACE
```

Find the region with this command:
```
ibmcloud ks region
```

for me:
```
REGION=us-south
```

and don't forget to login
```
ibmcloud cr login
```

```
IMAGE_PULL_SECRET_NAME=docker-credentials
TOKEN_PASS=$(ibmcloud cr token-add --description "kf-tutorial" --non-expiring -q)
kubectl --namespace default \
	  create secret docker-registry $IMAGE_PULL_SECRET_NAME \
	  --docker-server=registry.ng.bluemix.net \
	  --docker-username=token \
	  --docker-password=$TOKEN_PASS \
	  --docker-email=a@b.com
```
#### Build source images for serving

```
./s2i build . seldonio/seldon-core-s2i-python3:0.5 us.icr.io/$NAMESPACE/skmnistclassifier_runtime:0.1
docker push us.icr.io/$NAMESPACE/skmnistclassifier_runtime:0.1
```

### Step 6: Serve image.

Now we download the workflow and send it to argo. Please feel free to inspect it.

We wish we had the time to.

```
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/serving-sk-mnist-workflow.yaml
~/argo submit serving-sk-mnist-workflow.yaml -p docker-user=us.icr.io/$NAMESPACE -p deploy-model=true --serviceaccount seldon
```

And to check that it worked
```bash
trevor_d_grant@cloudshell:~ (kubeflow-hacky-hacky)$ ~/argo list
NAME                     STATUS      AGE   DURATION
seldon-sk-deploy-lfbzc   Succeeded   9s    3s
```


### Step 7: Testing

At this point, you can go ahead and test your deployment. Or grab a drink :)
