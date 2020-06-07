#!/usr/bin/env python
# coding: utf-8

# # Kubeflow pipeline
# This is a fairly simple pipeline, containing sequential steps:
#
# 1. Update data - implemented by lightbend/recommender-data-update-publisher:0.2 image
# 2. Run model training. Ideally we would run TFJob, but due to the current limitations for pipelines, we will directly use an image implementing training lightbend/ml-tf-recommender:0.1
# 3. Update serving model - implemented by lightbend/recommender-model-publisher:0.2

# # Setup

# In[1]:

get_ipython().system('pip install kubernetes --upgrade --user')
get_ipython().system('pip install kfp --upgrade --user')

# the Pipelines SDK.  This library is included with the notebook image.
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.notebook
from kubernetes import client as k8s_client

# # Create/Get an Experiment in the Kubeflow Pipeline System
# The Kubeflow Pipeline system requires an "Experiment" to group pipeline runs. You can create a new experiment, or call client.list_experiments() to get existing ones.

# In[3]:

client = kfp.Client()
client.list_experiments()
#exp = client.create_experiment(name='mdupdate')
exp = client.get_experiment(experiment_name='mdupdate')

# # Define a Pipeline
# Authoring a pipeline is like authoring a normal Python function. The pipeline function describes the topology of the pipeline.
#
# Each step in the pipeline is typically a ContainerOp --- a simple class or function describing how to interact with a docker container image. In the pipeline, all the container images referenced in the pipeline are already built.

# In[4]:


@dsl.pipeline(
    name='Recommender model update',
    description='Demonstrate usage of pipelines for multi-step model update')
def recommender_pipeline():
    # Load new data
    data = dsl.ContainerOp(
        name='updatedata',
        image='lightbend/recommender-data-update-publisher:0.2') \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_URL', value='http://minio-service.kubeflow.svc.cluster.local:9000')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_KEY', value='minio')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_SECRET', value='minio123'))
    # Train the model
    train = dsl.ContainerOp(
        name='trainmodel',
        image='lightbend/ml-tf-recommender:0.1') \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_URL', value='minio-service.kubeflow.svc.cluster.local:9000')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_KEY', value='minio')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_SECRET', value='minio123'))
    train.after(data)
    # Publish new model model
    publish = dsl.ContainerOp(
        name='publishmodel',
        image='lightbend/recommender-model-publisher:0.2') \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_URL', value='http://minio-service.kubeflow.svc.cluster.local:9000')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_KEY', value='minio')) \
      .add_env_variable(k8s_client.V1EnvVar(name='MINIO_SECRET', value='minio123')) \
      .add_env_variable(k8s_client.V1EnvVar(name='KAFKA_BROKERS', value='cloudflow-kafka-brokers.cloudflow.svc.cluster.local:9092')) \
      .add_env_variable(k8s_client.V1EnvVar(name='DEFAULT_RECOMMENDER_URL', value='http://recommendermodelserver.kubeflow.svc.cluster.local:8501')) \
      .add_env_variable(k8s_client.V1EnvVar(name='ALTERNATIVE_RECOMMENDER_URL', value='http://recommendermodelserver1.kubeflow.svc.cluster.local:8501'))
    publish.after(train)


# # Compile pipeline

# In[5]:

compiler.Compiler().compile(recommender_pipeline, 'pipeline.tar.gz')

# # Submit an experiment run

# In[6]:

run = client.run_pipeline(exp.id, 'pipeline1', 'pipeline.tar.gz')

# In[ ]:
