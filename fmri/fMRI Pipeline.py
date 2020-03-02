#!/usr/bin/env python
# coding: utf-8

# ## God damned this is stupid
# 
# But i guess you need to create the CRD for SparkApps first...
# 
# ```
# kubectl -n kubeflow create -f https://raw.githubusercontent.com/GoogleCloudPlatform/spark-on-k8s-operator/master/manifest/crds/sparkoperator.k8s.io_sparkapplications.yaml
# ```
# 
# Then 
# ```
# kubectl -n kubeflow get customresourcedefinitions | grep spark
# ```
# 
# to make sure its there...
# 
# Then you have to bless the `pipeline-runner` with the neccessary karma:
# 
# ```
# kubectl -n kubeflow edit clusterrole pipeline-runner
# ```
# 
# add
# 
# ```
# - apiGroups:
#   - "sparkoperator.k8s.io"
#   resources:
#   - sparkapplications
#   verbs:
#   - '*'
# ```
# at the bottom

# In[51]:


import kfp.dsl as dsl

container_manifest = {
    "apiVersion": "sparkoperator.k8s.io/v1beta2",
    "kind": "SparkApplication",
    "metadata": {
        "name": "fmri-example-phase3",
        "namespace": "kubeflow"
    },
  "spec": {
      "type": "Scala",
      "mode": "cluster",
      "image": "gcr.io/spark-operator/spark:v2.4.5",
      "imagePullPolicy": "Always",
      "mainClass": "org.rawkintrevo.dsvd.App",
      "mainApplicationFile": "local:///home/jovyan/dsvd-1.0-SNAPSHOT-jar-with-dependencies.jar",
      "sparkVersion": "2.4.5",
      "restartPolicy": {
        "type": "Never"
      },
      "volumes": [
        {"name": "datapvc",
          "hostPath": {
            "path": "/data",
            "type": "Directory"
          }
        }
      ],
        
  "driver": {
    "cores": 1,  
    "coreLimit": "1200m",  
    "memory": "512m",  
    "labels": {
      "version": "2.4.5",  
    },      
    "serviceAccount": "spark-operatoroperator-sa", # also try spark-operatoroperator-sa
    "volumeMounts": [
        {
            "name": "datapvc",
            "mountPath": "/data"
        }
    ] 
  },
  "executor": {
    "cores": 1,
    "instances": 2,
    "memory": "512m"  
  },    
  "labels": {
    "version": "2.4.5"
  },      
  "volumeMounts": [
    {
        "name": "datapvc",
        "mountPath": "/data"
    }
  ]
  }
}

@dsl.pipeline(
    name="fMRI Pipeline",
    description="No need to ask why."
)
def fmri_pipeline():
    vop = dsl.VolumeOp(
        name="datapvc",
        resource_name="newpvc",
        size="10Gi",
        modes=dsl.VOLUME_MODE_RWO
    )

    step1 = dsl.ContainerOp(
        name="generatedata",
        image="rawkintrevo/r-fmri-gen:latest",
        command=["Rscript", "/pipelines/component/src/program.R", "--out", "/data/synthetic"],
        pvolumes={"/data": vop.volume}
    )

    step2 = dsl.ContainerOp(
        name="prepdata",
        image="rawkintrevo/py-fmri-prep:0.2",
        command=["python", "/pipelines/component/src/program.py"],
        arguments=["/data/synthetic.nii.gz", "/data/s.csv"],
        pvolumes={"/data": step1.pvolume}
    )
    

    rop = dsl.ResourceOp(
        name="spark-scala-mahout-fmri",
        k8s_resource=container_manifest,
        action="create",  
    ).after(step2)

import kfp.compiler as compiler

compiler.Compiler().compile(fmri_pipeline,"fmri-pipeline.tar.gz")


# In[19]:


get_ipython().system('pwd')


# In[ ]:




