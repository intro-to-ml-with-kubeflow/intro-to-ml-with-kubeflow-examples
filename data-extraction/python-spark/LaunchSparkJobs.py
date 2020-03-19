#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip3 install --upgrade --user kfp')


# In[ ]:


import kfp


# In[ ]:


import kfp.dsl as dsl


# In[ ]:


# Use Kubeflow's built in Spark operator
#tag::launch_operator[]
resource = {
    "apiVersion": "sparkoperator.k8s.io/v1beta2",
    "kind": "SparkApplication",
    "metadata": {
        "name": "boop",
        "namespace": "kubeflow"
    },
  "spec": {
      "type": "Python",
      "mode": "cluster",
      "image": "gcr.io/boos-demo-projects-are-rad/kf-steps/kubeflow/myspark",
      "imagePullPolicy": "Always",
      "mainApplicationFile": "local:///job/job.py", # See the Dockerfile OR use GCS/S3/...
      "sparkVersion": "2.4.5",
      "restartPolicy": {
        "type": "Never"
      },
  "driver": {
    "cores": 1,  
    "coreLimit": "1200m",  
    "memory": "512m",  
    "labels": {
      "version": "2.4.5",  
    },      
    "serviceAccount": "spark-operatoroperator-sa", # also try spark-operatoroperator-sa
 },
  "executor": {
    "cores": 1,
    "instances": 2,
    "memory": "512m"  
  },    
  "labels": {
    "version": "2.4.5"
  },      
  }
}

@dsl.pipeline(
    name="local Pipeline",
    description="No need to ask why."
)
def local_pipeline():

    rop = dsl.ResourceOp(
        name="boop",
        k8s_resource=resource,
        action="create",
        success_condition="status.applicationState.state == COMPLETED"
    )
#end::launch_operator[]

import kfp.compiler as compiler

compiler.Compiler().compile(local_pipeline,"boop.zip")


# In[ ]:


client = kfp.Client()


# In[ ]:


my_experiment = client.create_experiment(name='boop-test-2')
my_run = client.run_pipeline(my_experiment.id, 'boop-test', 
  'boop.zip')


# In[ ]:




