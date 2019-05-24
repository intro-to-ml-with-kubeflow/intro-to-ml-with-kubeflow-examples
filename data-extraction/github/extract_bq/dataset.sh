#!/bin/bash

set -ex


export PROJECT=${PROJECT:=boos-demo-projects-are-rad}
export DATASET=${DATASET:=intro_to_ml_with_kf}
export BUCKET=${BUCKET:=kf-gh-demo}
export EXPIRATION=${EXPIRATION:259200}
export RUN_ID=${RUN_ID:1}

# Set up buckets and datasets
gsutil mb -p ${PROJECT}  -l us gs://${BUCKET}/ --retention ${EXPIRATION}s || true

bq --location=us \
   mk --dataset --default_table_expiration ${EXPIRATION} \
   --default_partition_expiration ${EXPIRATION} \
   --description kubeflow_pipeline_data ${PROJECT}:${DATASET} \
  || echo "BQ Dataset ${DATASET} exists re-using"

# Run all of the queries in the container.
# This way we can add more queries without changing our shell script.
for QUERY_NAME in $(ls *.bsql)
do
  # Strip out the trailing .bsql from the table name to comply with BQ restrictions
  TABLE_NAME="${RUN_ID}$(echo ${QUERY_NAME}| cut -d "." -f 1)"
  # Run the query
  bq query --location=us \
     --destination_table ${PROJECT}:${DATASET}.${TABLE_NAME} \
     --replace \
     --use_legacy_sql=false \
       "$(cat ${QUERY_NAME})"
  # And extract the result to avro
  echo "Extracting $TABLE"
  bq --location=us extract --destination_format=AVRO\
     "${PROJECT}:${DATASET}.${TABLE_NAME}" \
     # We use the * here so that we have multiple files, required for > 1GB
     "gs://${BUCKET}/data/${TABLE_NAME}/data-*.avro"
done
