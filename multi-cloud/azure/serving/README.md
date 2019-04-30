

## Check your Azure set up

You should already have your account & cluster set up.
If you don't you can go back to the `fast-start.sh` script and look at how it does the Azure set up.


**Note**: If you want you can deploy a new Kubeflow cluster on Azure and re-do the training (in versions prior to Kubeflow 0.5 we just use `--platform none`).
There is a guide at https://github.com/Microsoft/DeployDLKubeflowAKS you may want to take a look at. This is **optional** so only do this if you want.




## Copy your model somewhere you can access it from Azure

Right now your model is in an PV mount on GKE, but those aren't cross-cloud.
To make it cross-cloud we will use boto to upload our model to GCS/S3-compatable/[Azure Blob Storage](https://azure.microsoft.com/en-gb/services/storage/blobs/).

### Create your Azure Blob Storage

You can go to https://portal.azure.com/#blade/HubsExtension/BrowseResourceBlade/resourceType/Microsoft.Storage%2FStorageAccounts and create your blob storage.

Or with the cli:

```bash
az storage container create --name mystoragecontainer
```
### Push Model from GCP to your Cloud Storage

Now you've got the credentials you need! It's time to go ahead and clone our repo and get do a kind of hacky copy into our blob storage:

```bash
cd ~/
git clone https://github.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples.git
export WORKSHOP_HOME=~/intro-to-ml-with-kubeflow-examples
pushd $WORKSHOP_HOME/multi-cloud/hacky-s3-copy
```

#### Editing the hack s3 upload

Now this container is designed to copy into S3, and the Azure blob storage doesn't directly expose an S3 API. So you're going to need to go inside of the `Dockerfile` and add the `pip install azure-storage-blob` so that you have the library.

Now you're going to need to look inside of `beam-me-up-scotty.py` script and replace the use of boto with the `azure-storage-blob` library (and for now we'll just hard-code credientals as illustrated in the [Azure blob Python documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python).

**Note:** Normally you'd use secrets, but since this is going to be deprecated anyways we'll just hard code it.

#### Running the S3 upload


Now you can build and push this image, we have a template to run it called `hacky-s3-copy.yaml` that expects it to be at `gcr.io/$GOOGLE_PROJECT/hacky-s3-copy:oh-lord`.
If you get lost `solution7.sh` will show you how.


## Connect to your Azure AKS cluster

You can connect to your cluster:

```bash
az aks get-credentials --name azure-kf-test --resource-group westus
```

Make your an Azure container registry:
```bash
az acr create --resource-group myResourceGroup --name <myContainerRegistry> --sku Basic
```

Connect to Azure container registry:

```bash
az acr update -n <acrName> --admin-enabled true
docker login <myregistry>.azurecr.io
```

## Build source images for fetching the model & serving

```
./s2i build . seldonio/seldon-core-s2i-python3:0.5 <myregistry>.azurecr.io/skmnistclassifier_runtime:0.1
docker push <myregistry>.azurecr.io/skmnistclassifier_runtime:0.1
```

### Serve image:

Now we download the workflow and send it to argo. Please feel free to inspect it.

We wish we had the time to...

```bash
wget https://raw.githubusercontent.com/intro-to-ml-with-kubeflow/intro-to-ml-with-kubeflow-examples/master/multi-cloud/ibm/serving/serving-sk-mnist-workflow.yaml
~/argo submit serving-sk-mnist-workflow.yaml -p docker-user=<myregistry>.azurecr.io/ -p deploy-model=true --serviceaccount seldon
```

And to check that it worked
```bash
trevor_d_grant@cloudshell:~ (kubeflow-hacky-hacky)$ ~/argo list
NAME                     STATUS      AGE   DURATION
seldon-sk-deploy-lfbzc   Succeeded   9s    3s
```

And have party! Check the logs if you dare.
