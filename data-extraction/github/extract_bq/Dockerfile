# This image includes the gcloud command we need for export
# For a first run locally you will need to authenticate:
# docker run -ti --name gcloud-config --entrypoint "/doauth.sh" kf-steps/bq-extract:v2
# docker run --volumes-from gcloud-config google/cloud-sdk
# In GKE creds should already exist
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