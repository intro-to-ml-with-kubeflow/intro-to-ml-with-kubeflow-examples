#!/bin/bash
set -ex

# Minio runs on port 9000 (both UI and service) so expose locally to use cli or UI
#tag::fwdMinio[]
kubectl port-forward -n kubeflow svc/minio-service 9000:9000 &
#end::fwdMinio[]

# Give it a spell to settle
sleep 10

# Kubeflow creates a minio user with password minio123 at install
#tag::configMC[]
mc config host add minio http://localhost:9000 minio minio123
#end::configMC[]

#tag::listMC[]
mc ls minio
#end::listMC[]
# Output [2018-12-13 18:23:41 CST]     0B mlpipeline/

# Make a new bucket for our work
#tag::makeBucket[]
mc mb minio/kf-book-examples
#end::makeBucket[]
