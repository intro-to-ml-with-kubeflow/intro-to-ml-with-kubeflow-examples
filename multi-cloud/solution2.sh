#!/usr/bin/env bash

## Adding Seldon

# Now we install some extra components, which we need to do in the KS app directory
# We'll install seldon on Google for serving (don't worry we'll do it again elsewhere)
pushd ks_app
ks pkg install kubeflow/seldon
ks generate seldon seldon
# We can either use KS to apply this, or we can use kfctl to re-apply the app.
# We use kfctl, since Kubeflow is moving away from KS in the long term, but you
# may see other guides which say to do something like:
# ks apply default -c seldon
popd
# Applying to the cluster is done with kfctl.sh (although you could use ks directly too)
kfctl.sh apply k8s
# Optionally there are additional seldon components, like the analytics
