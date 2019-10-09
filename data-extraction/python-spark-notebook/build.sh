set -ex
TARGET=${TARGET:-"gcr.io/$GOOGLE_PROJECT/kubeflow/spark-notebook:v1"}
BASE=${BASE:-"gcr.io/kubeflow-images-public/tensorflow-2.0.0a-notebook-cpu:v0.5.0"}
docker build . -t "${TARGET}" --build-arg base=$BASE
docker push ${TARGET}
