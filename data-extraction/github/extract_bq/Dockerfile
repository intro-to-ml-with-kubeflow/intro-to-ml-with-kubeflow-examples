# For our base we use ubuntu because I'm lazy
FROM hub.docker.com/ubuntu:latest
# We tend to need UTF8
RUN apt-get update && apt-get install -y locales \
# Remove the cached apt lists because each run is a new layer
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
# Install the gcloud tool so we can dump the gh tables
RUN CLOUD_SDK_REPO="cloud-sdk-$(grep VERSION_CODENAME /etc/os-release | cut -d '=' -f 2)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y
COPY *.sh /
COPY *.bsql /
# Make our step semi-configurable
ARG project=boos-demo-projects-are-rad
ENV PROJECT=$project
ARG dataset=intro_to_ml_with_kf
ARG bucket=kf-gh-demo
ENV DATASET=$dataset
ENV BUCKET=$bucket
ENTRYPOINT ["dataset.sh"]