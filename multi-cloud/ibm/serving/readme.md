

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
```


### Step 2: Create Cloud Storage Service

### Step 3: Push Model from GCP to your Cloud Storage

see `../hacky-s3-copy`

### Step 4: Create K8s cluster on IBM

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
ks init ibm-serving-deployment --api-spec=version:v1.8.0
```

```bash
cd ibm-serving-deployment
ks registry add seldon-core github.com/SeldonIO/seldon-core/tree/master/seldon-core
ks pkg install seldon-core/seldon-core@master
ks generate seldon-core seldon-core
```


Apply everything

```
ks apply default
```


#### Download image serving files

```bash
mkdir ibm-serving
wget
```
#### Install s2i

s2i is a program that creates images out of source files.

```bash
wget https://github.com/openshift/source-to-image/releases/download/v1.1.13/source-to-image-v1.1.13-b54d75d3-linux-amd64.tar.gz
tar -xvf source-to-image-v1.1.13-b54d75d3-linux-amd64.tar.gz
```




### Step 6: Serve image.

