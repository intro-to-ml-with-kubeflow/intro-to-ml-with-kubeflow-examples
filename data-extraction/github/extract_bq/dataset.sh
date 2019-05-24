#!/bin/bash

set -ex


export PROJECT=${PROJECT:=boos-demo-projects-are-rad}
export DATASET=${DATASET:=intro_to_ml_with_kf}
export BUCKET=${BUCKET:=kf-gh-demo}


# Set up buckets and datasets
gsutil mb -p ${PROJECT}  -l us gs://${BUCKET}/ || true

bq --location=us \
   mk --dataset --default_table_expiration 3600000 \
   --default_partition_expiration 3600000 \
   --description stackoverflow_data ${PROJECT}:$DATASET || true

# Run all of the queries in the container.
# This way we can add more queries without changing our shell script.
for QUERY_NAME in $(ls *.bsql) do
	     # Run the query
	     bq query --location=us \
		--destination_table ${PROJECT}:${DATASET}.${QUERY_NAME} \
		--replace \
		--use_legacy_sql=false \
		"$(cat ${QUERY_NAME})"
	     # And extract the result to avro
	     echo "Extracting $TABLE"
	     bq --location=us extract --destination_format=AVRO\
		"${PROJECT}:${DATASET}.${QUERY_NAME}" \
		"gs://${BUCKET}/data/${QUERY_NAME}/data-*.avro"
done
