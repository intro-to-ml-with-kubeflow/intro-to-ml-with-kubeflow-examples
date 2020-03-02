#!/usr/bin/env python
# coding: utf-8

# # Installation and imports

# In[1]:


get_ipython().system('pip install kfmd --upgrade --user')
get_ipython().system('pip install pandas --upgrade --user')

from kfmd import metadata
import pandas
from datetime import datetime


# Create a workspace, run and execution

# In[2]:


ws1 = metadata.Workspace(
    # Connect to metadata-service in namesapce kubeflow in k8s cluster.
    backend_url_prefix="metadata-service.kubeflow.svc.cluster.local:8080",
    name="ws1",
    description="a workspace for testing",
    labels={"n1": "v1"})
r = metadata.Run(
    workspace=ws1,
    name="run-" + datetime.utcnow().isoformat("T") ,
    description="a run in ws_1",
)
exec = metadata.Execution(
    name = "execution" + datetime.utcnow().isoformat("T") ,
    workspace=ws1,
    run=r,
    description="execution example",
)


# Log data set, model and its evaluation

# In[3]:


data_set = exec.log_input(
        metadata.DataSet(
            description="an example data",
            name="mytable-dump",
            owner="owner@my-company.org",
            uri="file://path/to/dataset",
            version="v1.0.0",
            query="SELECT * FROM mytable"))
model = exec.log_output(
    metadata.Model(
            name="MNIST",
            description="model to recognize handwritten digits",
            owner="someone@kubeflow.org",
            uri="gcs://my-bucket/mnist",
            model_type="neural network",
            training_framework={
                "name": "tensorflow",
                "version": "v1.0"
            },
            hyperparameters={
                "learning_rate": 0.5,
                "layers": [10, 3, 1],
                "early_stop": True
            },
            version="v0.0.1",
            labels={"mylabel": "l1"}))
metrics = exec.log_output(
    metadata.Metrics(
            name="MNIST-evaluation",
            description="validating the MNIST model to recognize handwritten digits",
            owner="someone@kubeflow.org",
            uri="gcs://my-bucket/mnist-eval.csv",
            data_set_id=data_set.id,
            model_id=model.id,
            metrics_type=metadata.Metrics.VALIDATION,
            values={"accuracy": 0.95},
            labels={"mylabel": "l1"}))


# List all the models in the workspace

# In[4]:


pandas.DataFrame.from_dict(ws1.list(metadata.Model.ARTIFACT_TYPE_NAME))


# Get basic lineage

# In[5]:


print("model id is %s\n" % model.id)


# Find the execution that produces this model.

# In[6]:


output_events = ws1.client.list_events2(model.id).events
assert len(output_events) == 1
execution_id = output_events[0].execution_id
print(execution_id)


# Find all events related to that execution.

# In[7]:


all_events = ws1.client.list_events(execution_id).events
assert len(all_events) == 3
print("\nAll events related to this model:")
pandas.DataFrame.from_dict([e.to_dict() for e in all_events])


# In[ ]:




