

## Signing up for IBMCloud (formerly known as Bluemix)


1. [Create an IBMCloud Account](https://cloud.ibm.com/registration/). You Can skip this step if you already have one.

2. Then go to [here](https://strata-kubeflow.mybluemix.net/) to request a cluster.

    2a. Select `us-south`

3. You will be added to the IBM Lab account and granted access to a cluster. Note the name of your cluster. It will be something like: `strata_kubeflowXX`

4. Refresh your [IBMCloud Dashboard](https://cloud.ibm.com/)

5. Switch to the IBM account by clicking on the account selection drop down in the top nav bar.

6. Click on Kubernetes Clusters in the Resource Summary tile.

7. Under Kubernetes Clusters, click on the cluster that has been assigned to you.

8. Launch the Kubernetes Dashboard and have a look around! You can come back to this dashboard throughout your lab.

## Meanwhile back at the GCP cloud shell ranch...

We don't _need_ gcp shell, it just happens to be a good one and we already have
`ibmcloud` installed there. (If you don't, please see the first section in $INTRO_TO_ML_W_KUBEFLOW_EXAMPLES/multi-cloud/ibm/serving/readme.md)

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

That second command should show your cluster. Run this command, but replace `<my_cluster_name>` with the name of your cluster.
```
ibmcloud ks cluster-config <my_cluster_name>
```

For example, this was mine:

```
ibmcloud ks cluster-config strata-kubeflow02
```

which will spit out a line like:

```
export KUBECONFIG=/home/trevor_d_grant/.bluemix/plugins/container-service/clusters/strata-kubeflow02/kube-config-dal13-strata-kubeflow02.yml
```

and you need to copy and paste the line that was spit out and run that as well.

This lets kubectl know which cluster it is aimed at.

## Let's play kubeflow engineers

You probably have a lot of junk lying around your home directory- you could delete it all
but whatevs, lets just make a new dir

```
cd ~/
mkdir ibm-training
cd ibm-training
```

OK- let's make a Kubeflow App.  Please excuse us for not explaining in depth what each line is doing.
We assume you have completed this on GCS already, so this is just a review/example on IBM.

```
export KS_INIT_EXTRA_ARGS="--api-spec=version:v1.12.6"
## need this bc IBM throws a stupid `-IKS` on the end of the version. It's not a race car IBM...
kfctl.sh init ibm-app --platform none
cd ibm-app
source env.sh
kfctl.sh generate platform
kfctl.sh apply platform
kfctl.sh generate k8s
kfctl.sh apply k8s
```


Now we need to create a cluster role binding in this cluster (just like on gcp)
```
kubectl create clusterrolebinding sa-admin --clusterrole=cluster-admin --serviceaccount=kubeflow:default
```


Now persisten volume claims, have to claim something against a persistent volume.

In google, GCP handles this, but in IBM we have to declare our own Persistent Volume to
be claimed against.

to do that download this file:

```
cd ~/
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/training/pv-volume.yaml
```

Now, here's the tricky part. You have update the yaml and change the path to whatever you get when you run these commands
```
cd ~/
pwd
```

Then
```
pico pv-volume.yaml
```

and change the last line.
(Also, I'm not sure if this is nessicary or I'm cargo culting, but it does seem to make it all work).


Finally we also are going to create the persistent volume claim where the model will be stored and submit the job.

```
kubectl create -f https://raw.githubusercontent.com/rawkintrevo/intro-to-ml-with-kubeflow-examples/master/multi-cloud/config/pv-claim.yaml
cd ~/example-seldon/workflows
argo submit training-sk-mnist-workflow.yaml -n kubeflow
```

To check it:
```
argo list -n kubeflow
```

At this point its just like gcp.

Also this takes about 60 seconds to run, so if it hasn't completed by then- time to start bug shooting.
