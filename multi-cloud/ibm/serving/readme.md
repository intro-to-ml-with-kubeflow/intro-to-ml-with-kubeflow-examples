

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

Should only take 20 minutes or so-


### Step 5: Install Seldon Core

#### Install seldon-core



#### Install s2i

### Step 6: Serve image.

