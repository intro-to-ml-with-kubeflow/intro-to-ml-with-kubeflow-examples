#!/bin/bash
# Note: this only works inside of cloudshell!
#tag::cloudshell_script[]
G_SOURCES="https://source.developers.google.com/p"
cloudshell_open \
  --repo_url "$G_SOURCES/$PROJECTID/r/$PROJECTID-$DEPLOYMENTNAME-config"\
  --dir"v$KUBEFLOWVERSION/kubeflow/kf_util" \
  --page "editor" \
  --tutorial "conn.md"
#end::cloudshell_script[]
