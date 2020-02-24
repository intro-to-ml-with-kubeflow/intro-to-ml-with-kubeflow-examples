#!/bin/bash
# Build a notebook with Spark
set -ex
V=${V:-"12"}
REPO=${REPO:-"gcr.io/$PROJECT"}
TARGET=${TARGET:-"$REPO/kubeflow/spark-notebook:v$V"}
BASE=${BASE:-"gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-cpu:1.0.0"}
docker build . -t "${TARGET}" --build-arg base=$BASE
docker push "${TARGET}"
# Build Spark worker image
SPARK_TARGET=${SPARK_TARGET:-"$REPO/kubeflow/spark-worker"}
tmp_dir=$(mktemp -d -t spark-build-XXXXXXXXXX)
pushd ${tmp_dir}
# Sometimes the US mirror fails
wget https://www-us.apache.org/dist/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz || wget https://www-eu.apache.org/dist/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvf spark-2.4.5-bin-hadoop2.7.tgz
pushd spark-2.4.5-bin-hadoop2.7
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v2.4.5 -b java_image_tag=8 build
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v2.4.5 push
popd
popd
# Add GCS to Spark images
docker build --build-arg base=$SPARK_TARGET/spark:v2.4.5 -t "${SPARK_TARGET}/spark-with-gcs:v2.4.5-$V" -f AddGCSDockerfile .
docker build --build-arg base=$SPARK_TARGET/spark-r:v2.4.5 -t "${SPARK_TARGET}/spark-r-with-gcs:v2.4.5-$V" -f AddGCSDockerfile .
PYSPARK_WITH_GCS="${SPARK_TARGET}/spark-py-with-gcs:v2.4.5-$V"
docker build --build-arg base=$SPARK_TARGET/spark-py:v2.4.5 -t ${PYSPARK_WITH_GCS} -f AddGCSDockerfile .
# Add Python 3.6 to Spark images
SPARK_PY36_WORKER="${SPARK_TARGET}/spark-py-36:v2.4.5-$V"
docker build --build-arg base=${PYSPARK_WITH_GCS} -t ${SPARK_PY36_WORKER} -f AddPython3.6Dockerfile .

docker push "${SPARK_TARGET}/spark-with-gcs:v2.4.5-$V"
docker push "${SPARK_TARGET}/spark-r-with-gcs:v2.4.5-$V"
docker push "${SPARK_TARGET}/spark-py-with-gcs:v2.4.5-$V"
docker push "${SPARK_PY36_WORKER}"
rm -rf ${tmp_dir}

echo "Spark notebook pushed to ${TARGET}"
echo "Spark py worker pushed to ${SPARK_PY36_WORKER}"
