#!/bin/bash
set -ex

SPARK_DEMO_DIR=${SPARK_DEMO_DIR:=~/spark_demo_2}
SPARK_LR_DIR="$(pwd)/lr_demo"
SPARK_DEMO_GCS=${SPARK_DEMO_GCS:=gs://boo-spark-kf-demo}

# Set up kubeflow
mkdir $SPARK_DEMO_DIR
pushd $SPARK_DEMO_DIR
pwd

wget https://raw.githubusercontent.com/kubeflow/kubeflow/master/scripts/download.sh
chmod a+x download.sh
KUBEFLOW_VERSION=0.5.0
export KUBEFLOW_VERSION
./download.sh

PATH="$(pwd)/scripts":$PATH
kfctl.sh init mydemoapp --platform gcp
pushd mydemoapp
source env.sh
kfctl.sh generate platform
kfctl.sh apply platform
kfctl.sh generate k8s
kfctl.sh apply k8s
pushd ks
# Set up the Spark operator
ks pkg install kubeflow/spark
ks generate spark-operator spark-operator --name=spark-operator
ks apply default -c spark-operator

# Create a Spark job with the operator (Pi)
ks generate spark-job spark-pi --name=spark-operator \
   --applicationResource="local:///opt/spark/examples/jars/spark-examples_2.11-2.3.1.jar" \
   --mainClass=org.apache.spark.examples.SparkPi
ks apply default -c spark-pi

# Create a Spark job with the operator to train an LR model

pushd $SPARK_MNIST_DIR
sbt assembly
gsutil cp target/scala-2.11/basic.lr-assembly-0.0.1.jar "$SPARK_DEMO_GCS/jars"
gsutil cp sample.csv "$SPARK_DEMO_GCS/input/part0.csv"
popd

ks generate spark-job spark-lr --name=spark-operator \
   --applicationResource="$SPARK_DEMO_GCS/jars/basic.lr-assembly-0.0.1.jar" \
   --mainClass=com.introtomlwithkubeflow.spark.demo.lr.TrainingApp
   "$SPARK_DEMO_GCS/input" "$SPARK_DEMO_GCS/output"
ks apply default -c spark-lr


# Create a Spark job with the operator for data prep on the GitHub data

popd
