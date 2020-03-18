#!/usr/bin/env python
# coding: utf-8

# We start by downloading a specific release of the components because running from master is not a good way to buid "repetable" systems

# In[ ]:


get_ipython().system('wget https://github.com/kubeflow/pipelines/archive/0.2.5.tar.gz')


# In[ ]:


get_ipython().system('tar -xvf 0.2.5.tar.gz')


# In[ ]:


import kfp


# In[ ]:





# In[ ]:


#tag::loadGCSDLComponent[]
gcs_download_component = kfp.components.load_component_from_file(
    "pipelines-0.2.5/components/google-cloud/storage/download/component.yaml")
#end::loadGCSDLComponent[]
#tag::loadTFDVAndFriendsComponents[]
tfx_csv_gen = kfp.components.load_component_from_file(
    "pipelines-0.2.5/components/tfx/ExampleGen/CsvExampleGen/component.yaml")
tfx_statistic_gen = kfp.components.load_component_from_file(
    "pipelines-0.2.5/components/tfx/StatisticsGen/component.yaml")
tfx_schema_gen = kfp.components.load_component_from_file(
    "pipelines-0.2.5/components/tfx/SchemaGen/component.yaml")
tfx_example_validator = kfp.components.load_component_from_file(
    "pipelines-0.2.5/components/tfx/ExampleValidator/component.yaml")
#end::loadTFDVAndFriendsComponents[]


# In[ ]:


@kfp.dsl.pipeline(
  name='DL',
  description='Sample DL pipeline'
)
def pipeline_with_dl():
    #tag::dlOp[]
    dl_op = gcs_download_component(
        gcs_path="gs://ml-pipeline-playground/tensorflow-tfx-repo/tfx/components/testdata/external/csv") # Your path goes here
    #end::dlOp[]


# In[ ]:


kfp.compiler.Compiler().compile(pipeline_with_dl, 'dl_pipeline.zip')


# In[ ]:


client = kfp.Client()


# In[ ]:


my_experiment = client.create_experiment(name='dl')
my_run = client.run_pipeline(my_experiment.id, 'dl', 
  'dl_pipeline.zip')


# In[ ]:


#tag::standaloneTFDVPipeline[]
@kfp.dsl.pipeline(
  name='TFDV',
  description='TF DV Pipeline'
)
def tfdv_pipeline():
    # DL with wget, can use gcs instead as well
    #tag::wget[]
    fetch = kfp.dsl.ContainerOp(
      name='download',
      image='busybox',
      command=['sh', '-c'],
      arguments=[
          'sleep 1;'
          'mkdir -p /tmp/data;'
          'wget https://raw.githubusercontent.com/moorissa/medium/master/items-recommender/data/trx_data.csv -O /tmp/data/results.csv'],
      file_outputs={'downloaded': '/tmp/data'})
    # This expects a directory of inputs not just a single file
    #end::wget[]
    #tag::csv[]
    records_example = tfx_csv_gen(input_base=fetch.output)
    #end::csv[]
    #tag::stats[]
    stats = tfx_statistic_gen(input_data=records_example.output)
    #end::stats[]
    #tag::schema[]
    schema_op = tfx_schema_gen(stats.output)
    #end::schema[]
    #tag::validate[]
    tfx_example_validator(stats=stats.outputs['output'], schema=schema_op.outputs['output'])
    #end::validate[]
#end::standaloneTFDVPipeline[]


# In[ ]:


kfp.compiler.Compiler().compile(tfdv_pipeline, 'tfdv_pipeline.zip')


# In[ ]:


my_experiment = client.create_experiment(name='tfdv_pipeline')
my_run = client.run_pipeline(my_experiment.id, 'tfdv', 
  'tfdv_pipeline.zip')


# In[ ]:


get_ipython().system('pip3 install tfx tensorflow-data-validation')


# In[ ]:


#tag::importTFDV[]
import tensorflow_data_validation as tfdv
#end::importTFDV[]


# You can download your schema by looking at the inputs/outputs in your pipeline run for the schema gen stage

# In[ ]:


#tag::displaySchema{}
schema = tfdv.load_schema_text("schema_info_2")
tfdv.display_schema(schema)
#end::displaySchema[]


# In[ ]:




