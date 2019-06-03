#!/bin/bash

set -ex


export PROJECT=${PROJECT:=boos-demo-projects-are-rad}
export DATASET=${DATASET:=intro_to_ml_with_kf}
export BUCKET=${BUCKET:=kf-gh-demo}
export EXPIRATION=${EXPIRATION:=259200}
export RUN_ID=${RUN_ID:=1}

# If we have a SA file activate it
if [[ ! -z ${GOOGLE_APPLICATION_CREDENTIALS} &&  -f ${GOOGLE_APPLICATION_CREDENTIALS} ]]; then
  gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
else
  echo "No SA found (checked ${GOOGLE_APPLICATION_CREDENTIALS})"
fi

if ! GOOGLE_PROJECT=$(gcloud config get-value project 2>/dev/null) ||
    [ -z "$GOOGLE_PROJECT" ]; then
  echo "Default project not configured. Press enter to auto-configure or Ctrl-D to exit"
  latest_project=$(gcloud projects list | tail -n 1 | cut -f 1  -d' ')
  gcloud config set project "$latest_project"
fi

# Set up buckets and datasets
gsutil ls gs://${BUCKET}/ || gsutil mb -p ${PROJECT}  -l us --retention ${EXPIRATION}s gs://${BUCKET}/  

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
     "$(cat ${QUERY_NAME})" &
  query_pid=$!
  echo "${query_pid}" > ${QUERY_NAME}.pid
done
for QUERY_NAME in $(ls *.bsql)
do
  wait $(cat ${QUERY_NAME}.pid)
  rm ${QUERY_NAME}.pid
  # And extract the result to avro
  echo "Extracting $TABLE"
  # We use the * here so that we have multiple files, required for > 1GB
  bq --location=us extract --destination_format=AVRO\
     "${PROJECT}:${DATASET}.${TABLE_NAME}" \
     "gs://${BUCKET}/data/${TABLE_NAME}/data-*.avro" &
  echo "${query_pid}" > ${QUERY_NAME}.export_pid
done
# Wait for all the table exports to finish. If we wait on all it eats the errors
for QUERY_NAME in $(ls *.bsql)
do
  wait $(cat ${QUERY_NAME}.export_pid)
  rm ${QUERY_NAME}.export_pid
done
