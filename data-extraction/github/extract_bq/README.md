This step can be built locally:

``bash
docker-compose build
```

Then you can run it locally:

```bash
docker run -ti --name gcloud-config --entrypoint "/doauth.sh" kf-steps/bq-extract:v2
docker run --volumes-from gcloud-config google/cloud-sdk
```

To run it in Kubeflow:

```bash
# Push image
docker tag kf-steps/bq-extract:v8 gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v8
docker push gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v8
cd default
# Generate & run job
kustomize edit add configmap github-data-extract --from-literal=projectName=${PROJECT_NAME}
kustomize build . | kubectl apply -f -
# Verify the job:
kubectl get jobs |grep gh-data
```