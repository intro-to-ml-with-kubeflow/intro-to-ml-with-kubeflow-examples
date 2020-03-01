#!/bin/bash


# Minio runs on port 9000 (both UI and service) so expose locally to use cli or UI
kubectl port-forward -n kubeflow svc/minio-service 9000:9000 &

# Kubeflow creates a minio user with password minio123 at install
mc config host add minio http://localhost:9000 minio minio123

mc ls minio
# Output [2018-12-13 18:23:41 CST]     0B mlpipeline/

# Make a new bucket for our work
minio mb kf-book-examples
