#!/bin/bash
# Note: this only works inside of cloudshell!
#tag::cloudshell_script[]
cloudshell_open --repo_url "https://source.developers.google.com/p/$PROJECTID/r/$PROJECTID-$DEPLOYMENTNAME-config" --dir"v$KUBEFLOWVERSION/kubeflow/kf_util" --page "editor" --tutorial "conn.md"
#end::cloudshell_script[]
