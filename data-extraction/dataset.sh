#!/bin/bash

set -ex


export PROJECT=${PROJECT:=boos-demo-projects-are-rad}
export DATASET=intro_to_ml_with_kf_4
export BUCKET=${BUCKER:=kf-gh-demo}


# Set up buckets and datasets
gsutil mb -p ${PROJECT}  -l us gs://${BUCKET}/ || true

bq --location=us \
   mk --dataset --default_table_expiration 3600000 \
   --default_partition_expiration 3600000 \
   --description stackoverflow_data ${PROJECT}:$DATASET || true

# These parts belong in a KF pipeline, we'll cover them next
bq query --location=us \
   --destination_table ${PROJECT}:${DATASET}.stackoverflow \
   --replace \
   --use_legacy_sql=false \
   `cat stack_overflow_questions.bsql`

bq query --location=us \
   --destination_table ${PROJECT}:${DATASET}.github_comments \
   --replace \
   --use_legacy_sql=false \
   `cat github_comments_query_r2.bsql`

bq query --location=us \
   --destination_table ${PROJECT}:${DATASET}.github_issues \
   --replace \
   --use_legacy_sql=false \
   `cat github_issues_query.bsql`

# And extract to avro
for TABLE in "github_issues" "github_comments" "stackoverflow"
do
  echo "Extracting $TABLE"
  bq --location=us extract --destination_format avro\
     ${PROJECT}:${DATASET}.${TABLE} gs://${BUCKET}/data/${TABLE}
done
