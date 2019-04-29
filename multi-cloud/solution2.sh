#!/usr/bin/env bash

## Adding Seldon
export G_KF_APP=${G_KF_APP:="g-kf-app"}
pushd ~/$G_KF_APP
# Now we install some extra components, which we need to do in the KS app directory
# We'll install seldon on Google for serving (don't worry we'll do it again elsewhere)
pushd ks_app
ks pkg install kubeflow/seldon
ks generate seldon seldon
# We can either use KS to apply this, or we can use kfctl to re-apply the app.
# We use kfctl, since Kubeflow is moving away from KS in the long term, but you
# may see other guides which say to do something like:
ks apply default -c seldon
popd
popd
# Optionally there are additional seldon components, like the analytics, we cover them in solution2b
