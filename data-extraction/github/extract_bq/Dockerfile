# See build_manual.sh
#tag::base[]
FROM google/cloud-sdk:247.0.0
# Copy over the shell script and queries
COPY *.sh /
COPY *.bsql /
#end::base[]
# Make our step semi-configurable
ARG project=boos-demo-projects-are-rad
ENV PROJECT=$project
ARG dataset=intro_to_ml_with_kf
ARG bucket=kf-gh-demo
ENV DATASET=$dataset
ENV BUCKET=$bucket
#tag::base[]
VOLUME ["/root/.config"]
ENTRYPOINT ["/dataset.sh"]
#end::base[]