

## Get yer IBM on

TODO: This part should be moved to its own readme-

1. [create acct](https://cloud.ibm.com/registration/)

2. Then go to [here](https://strata-kubeflow.mybluemix.net/) to request a cluster.

    2a. Select `us-south`

3. You will be added to the IBM Lab account and granted access to a cluster. Note the name of your cluster. It will be something like: `myclusterXX`

4. Refresh your [IBMCloud Dashboard](https://cloud.ibm.com/)

5. Switch to the IBM account by clicking on the account selection drop down in the top nav bar.

6. Click on Kubernetes Clusters in the Resource Summary tile.

7. Under Kubernetes Clusters, click on the cluster that has been assigned to you.

8. Launch the Kubernetes Dashboard and have a look around! You can come back to this dashboard throughout your lab.

## Meanwhile back at the GCP cloud shell ranch...

We don't _need_ gcp shell, it just happens to be a good one and we already have
`ibmcloud` installed there.

Login in again.

```
ibmcloud login
```

This time its going to have you select an account.  Make sure to allign the account with
the one where your cluster is at, and select `us-south` for the region.

We need to "aim" our `kubectl at this cluster.

```
ibmcloud ks region-set us-south  # yes- you need to do it here too, or at least trevor did
ibmcloud ks clusters
```

That second command should show your cluster.

```
ibmcloud ks cluster-config strata-kubeflow02
```

which will spit out a line like:

```
export KUBECONFIG=/home/trevor_d_grant/.bluemix/plugins/container-service/clusters/strata-kubeflow02/kube-config-dal13-strata-kubeflow02.yml
```

and you need to run that as well.

## Let's play kubeflow engineers

You probably have a lot of junk lying around your home directory- you could delete it all
but whatevs, lets just make a new dir

```
mkdir ibm-training
cd ibm-training
```

OK- let's make a Kubeflow App

```
export KS_INIT_EXTRA_ARGS="--api-spec=version:v1.12.6"
## need this bc IBM throws a stupid `-IKS` on the end of the version. It's not a race car IBM...
kfctl.sh init ibm-app --platform none
cd ibm-app
source env.sh
wget https://raw.githubusercontent.com/kubernetes/kubernetes/v1.12.6/api/openapi-spec/swagger.json
kfctl.sh generate platform
kfctl.sh apply platform
kfctl.sh generate k8s
kfctl.sh apply k8s
```


TODO- remember we want ks-0.13 not 11
wget https://github.com/ksonnet/ksonnet/releases/download/v0.13.1/ks_0.13.1_linux_amd64.tar.gz
tar -xzf ks_0.13.1_linux_amd64.tar.gz

Hopefully that all worked.
```
kubectl create clusterrolebinding sa-admin --clusterrole=cluster-admin --serviceaccount=kubeflow:default

kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml
cd ~/example-seldon/workflows
argo submit training-sk-mnist-workflow.yaml -n kubeflow
```


To check it:
```
argo list -n kubeflow
```

At this point its just like gcp.
