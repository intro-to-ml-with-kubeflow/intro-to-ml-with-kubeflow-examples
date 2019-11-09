#!/bin/bash
# Build a notebook with Spark
set -ex
V=${V:-"3"}
REPO=${REPO:-"gcr.io/$GOOGLE_PROJECT"}
TARGET=${TARGET:-"$REPO/kubeflow/spark-notebook:v$V"}
BASE=${BASE:-"gcr.io/kubeflow-images-public/tensorflow-2.0.0a-notebook-cpu:v0.5.0"}
docker build . -t "${TARGET}" --build-arg base=$BASE
docker push "${TARGET}"
# Build Spark worker image
SPARK_TARGET=${SPARK_TARGET:-"$REPO/kubeflow/spark-worker"}
mkdir /tmp/spark-build
pushd /tmp/spark-build
wget https://www-us.apache.org/dist/spark/spark-2.4.4/spark-2.4.4-bin-hadoop2.7.tgz
tar -xvf spark-2.4.4-bin-hadoop2.7.tgz
pushd spark-2.4.4-bin-hadoop2.7
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v2.4.4 build
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v2.4.4 push
popd
popd
# Add GCS to Spark images
docker build --build-arg base=$SPARK_TARGET/spark:v2.4.4 -t "${SPARK_TARGET}/spark-with-gcs:v2.4.4-$V" -f AddGCSDockerfile .
docker build --build-arg base=$SPARK_TARGET/spark-r:v2.4.4 -t "${SPARK_TARGET}/spark-r-with-gcs:v2.4.4-$V" -f AddGCSDockerfile .
docker build --build-arg base=$SPARK_TARGET/spark-py:v2.4.4 -t "${SPARK_TARGET}/spark-py-with-gcs:v2.4.4-$V" -f AddGCSDockerfile .
docker push "${SPARK_TARGET}/spark-with-gcs:v2.4.4-$V"
docker push "${SPARK_TARGET}/spark-r-with-gcs:v2.4.4-$V"
docker push "${SPARK_TARGET}/spark-py-with-gcs:v2.4.4-$V"
