#!/bin/bash
# Build a notebook with Spark 3
# Note when Spark 3 is fully released we can use gcr.io/spark-operator/spark-py:v3.0.0
set -ex
V=${V:-"23"}
REPO=${REPO:-"gcr.io/$PROJECT"}
TARGET=${TARGET:-"$REPO/kubeflow/spark-notebook:v$V"}
BASE=${BASE:-"gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-cpu:1.0.0"}
SPARK_VERSION="3.0.0-preview2"
SPARK_RELEASE="spark-3.0.0-preview2-bin-hadoop3.2"
SPARK_ARTIFACT="${SPARK_RELEASE}.tgz"
docker build . -t "${TARGET}" --build-arg sparkversion="${SPARK_VERSION}" --build-arg sparkrelease="${SPARK_RELEASE}" --build-arg base="${BASE}"
docker push "${TARGET}"
# Build Spark worker image
SPARK_TARGET=${SPARK_TARGET:-"$REPO/kubeflow/spark-worker"}
if [ ! -f /tmp/${SPARK_ARTIFACT} ]; then
  pushd /tmp/
  # Sometimes the US mirror fails
  wget http://mirrors.ibiblio.org/apache/spark/spark-${SPARK_VERSION}/${SPARK_ARTIFACT} || \
    wget https://www-us.apache.org/dists/spark/spark-${SPARK_VERSION}/${SPARK_ARTIFACT} || \
    wget https://www-eu.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_ARTIFACT}
  popd
fi

tmp_dir=$(mktemp -d -t spark-build-XXXXXXXXXX)
pushd ${tmp_dir}
tar -xvf /tmp/${SPARK_ARTIFACT}

pushd ${SPARK_RELEASE}
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v${SPARK_VERSION}-${V} build
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v${SPARK_VERSION}-${V} -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
./bin/docker-image-tool.sh -r $SPARK_TARGET -t v${SPARK_VERSION}-${V} push
popd

popd
# Add GCS to Spark images
docker build --build-arg base=$SPARK_TARGET/spark:v${SPARK_VERSION}-${V} -t "${SPARK_TARGET}/spark-with-gcs:v${SPARK_VERSION}-$V" -f AddGCSDockerfile .
PYSPARK_WITH_GCS="${SPARK_TARGET}/spark-py-with-gcs:v${SPARK_VERSION}-$V"
docker build --build-arg base=$SPARK_TARGET/spark-py:v${SPARK_VERSION}-${V} -t ${PYSPARK_WITH_GCS} -f AddGCSDockerfile .
# Add Python 3.6 to PySpark images for notebook compat
SPARK_PY36_WORKER="${SPARK_TARGET}/spark-py-36:v${SPARK_VERSION}-$V"
docker build --build-arg base=${PYSPARK_WITH_GCS} -t ${SPARK_PY36_WORKER} -f AddPython3.6Dockerfile .

docker push "${SPARK_TARGET}/spark-with-gcs:v${SPARK_VERSION}-$V"
docker push "${SPARK_TARGET}/spark-py-with-gcs:v${SPARK_VERSION}-$V"
docker push "${SPARK_PY36_WORKER}"
rm -rf ${tmp_dir}

echo "Spark notebook pushed to ${TARGET}"
echo "Spark py worker pushed to ${SPARK_PY36_WORKER}"
