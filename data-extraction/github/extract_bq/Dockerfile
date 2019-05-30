# Please build with docker-compose build
# This image includes the gcloud command we need for export
# To build this use docker compose:
#
# docker-compose build
#
# For a first run locally you will need to authenticate:
#
# docker run -ti --name gcloud-config --entrypoint "/doauth.sh" kf-steps/bq-extract:v2
# docker run --volumes-from gcloud-config google/cloud-sdk
#
# In "production" we'll want to push our container to our repo:
#
# docker tag kf-steps/bq-extract:v7 gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v7
# docker push gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v7
#
# Then generate a job:
#
# cd default
# kustomize edit add configmap github-data-extract --from-literal=projectName=${PROJECT_NAME}
# kustomize generate . | kubectl apply -f -
# You can either add https://www.googleapis.com/auth/bigquery to the user-gcp-sa account
# TODO
# Manually run on this:
# kubectl run kf-steps bq-extract --image=gcr.io/${PROJECT_NAME}/kf-steps/bq-extract:v4 --namespace=kubeflow
FROM google/cloud-sdk:247.0.0
# Copy over the shell script and queries
COPY *.sh /
COPY *.bsql /
# Make our step semi-configurable
ARG project=boos-demo-projects-are-rad
ENV PROJECT=$project
ARG dataset=intro_to_ml_with_kf
ARG bucket=kf-gh-demo
ENV DATASET=$dataset
ENV BUCKET=$bucket
VOLUME ["/root/.config"]
ENTRYPOINT ["/dataset.sh"]