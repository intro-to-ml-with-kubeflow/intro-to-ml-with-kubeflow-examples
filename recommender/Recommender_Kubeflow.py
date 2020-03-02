#!/usr/bin/env python
# coding: utf-8

# # This is implementation of the Recommender training
# 
# This implementation takes a list of users and their purchasing history to calculate prediction
# on the probability that they would by a certain product.
# The implementation is structured in 2 parts:
# 1. Build rating matrix based on the purchasing history. The implementation is based on this blog post
# https://medium.com/datadriveninvestor/how-to-build-a-recommendation-system-for-purchase-data-step-by-step-d6d7a78800b6
# 2. Build collabarative filtering model based on the rating matrix. The implementation is based on this project https://github.com/Piyushdharkar/Collaborative-Filtering-Using-Keras 
# 
# Implementation is leveraging Minio for storing both source data and result models
# 
# It also uses Python kubernetes client for re starting model server pod
# 

# # 1. Install libraries

# In[1]:


get_ipython().system('pip install pandas --upgrade --user')
get_ipython().system('pip install keras --upgrade --user')
get_ipython().system('pip install minio --upgrade --user')
get_ipython().system('pip install kubernetes --upgrade --user')
get_ipython().system('pip install kfmd --upgrade --user')


# ## imports

# In[2]:


import pandas as pd
import numpy as np
import time
from minio import Minio
from keras.models import Model
from keras.layers import *
from keras.losses import *
import tensorflow as tf
import os
from kfmd import metadata
from datetime import datetime
from keras import backend as K
from kubernetes import client as k8s_client, config as k8s_config


# Create a workspace, run and execution

# In[3]:


execTime = datetime.utcnow().isoformat("T")
ws = metadata.Workspace(
    # Connect to metadata-service in namesapce kubeflow in k8s cluster.
    backend_url_prefix="metadata-service.kubeflow.svc.cluster.local:8080",
    name="recommender",
    description="a workspace for saving recommender experiments")
r = metadata.Run(
    workspace=ws,
    name="run-" + execTime ,
    description="recommender run",
)
exec = metadata.Execution(
    name = "execution" + execTime ,
    workspace=ws,
    run=r,
    description="recommender ML execution",
)


# # 2. Read data
# 
# For reading data we are using two diffierent approaches:
# 1. We use Tensorflow build in support to write resulting model to Minio
# 2. We use Minio APIs to read source data using Pandas. We could of use Boto APIs here instead.

# In[4]:


minio_endpoint = os.environ.get('MINIO_URL', 'minio-service.kubeflow.svc.cluster.local:9000')
minio_key = os.environ.get('MINIO_KEY', 'minio')
minio_secret = os.environ.get('MINIO_SECRET', 'minio123')

print('Minio parameters : URL ', minio_endpoint, ' key ', minio_key, ' secret ', minio_secret)

os.environ['AWS_ACCESS_KEY_ID'] = minio_key
os.environ['AWS_SECRET_ACCESS_KEY'] = minio_secret
os.environ['AWS_REGION'] = 'us-west-1'
os.environ['S3_REGION'] = 'us-west-1'
os.environ['S3_ENDPOINT'] = minio_endpoint
os.environ['S3_USE_HTTPS'] = '0'
os.environ['S3_VERIFY_SSL'] = '0'


# In[5]:


minioClient = Minio(minio_endpoint,
                    access_key=minio_key,
                    secret_key=minio_secret,
                    secure=False)

minioClient.fget_object('data', 'recommender/users.csv', '/tmp/users.csv')
customers = pd.read_csv('/tmp/users.csv')
minioClient.fget_object('data', 'recommender/transactions.csv', '/tmp/transactions.csv')
transactions = pd.read_csv('/tmp/transactions.csv')

#Log experiment data set
data_set = exec.log_input(
        metadata.DataSet(
            description="recommender current transactions and customers",
            name="Current transactions and customers",
            version=execTime,
            uri="minio:/tmp/transactions.csv; minio:/tmp/users.csv"))


# In[6]:


print(customers.shape)
customers.head()


# In[7]:


print(transactions.shape)
transactions.head()


# # 3 Data preparation
# 
# Our goal here is to break down each list of items in the products column into rows 
# and count the number of products bought by a user

# In[8]:


# 1: split product items
transactions['products'] = transactions['products'].apply(lambda x: [int(i) for i in x.split('|')])
transactions.head(2).set_index('customerId')['products'].apply(pd.Series).reset_index()


# In[9]:


# 2: organize a given table into a dataframe with customerId, single productId, and purchase count
pd.melt(transactions.head(2).set_index('customerId')['products'].apply(pd.Series).reset_index(), 
             id_vars=['customerId'],
             value_name='products') \
    .dropna().drop(['variable'], axis=1) \
    .groupby(['customerId', 'products']) \
    .agg({'products': 'count'}) \
    .rename(columns={'products': 'purchase_count'}) \
    .reset_index() \
    .rename(columns={'products': 'productId'})


# ## 3.1 Create data with user, item, and target field

# In[10]:


data = pd.melt(transactions.set_index('customerId')['products'].apply(pd.Series).reset_index(), 
             id_vars=['customerId'],
             value_name='products') \
    .dropna().drop(['variable'], axis=1) \
    .groupby(['customerId', 'products']) \
    .agg({'products': 'count'}) \
    .rename(columns={'products': 'purchase_count'}) \
    .reset_index() \
    .rename(columns={'products': 'productId'})
data['productId'] = data['productId'].astype(np.int64)

print(data.shape)
data.head()


# ## 3.2 Normalize item values across users

# In[11]:


df_matrix = pd.pivot_table(data, values='purchase_count', index='customerId', columns='productId')
df_matrix.head()


# In[12]:


df_matrix_norm = (df_matrix-df_matrix.min())/(df_matrix.max()-df_matrix.min())
print(df_matrix_norm.shape)
df_matrix_norm.head()


# In[13]:


# create a table for input to the modeling

d = df_matrix_norm.reset_index()
d.index.names = ['scaled_purchase_freq']
data_norm = pd.melt(d, id_vars=['customerId'], value_name='scaled_purchase_freq').dropna()
print(data_norm.shape)
data_norm.head()


# # 4 Preparing data for learning

# In[14]:


customer_idxs = np.array(data_norm.customerId, dtype = np.int)
product_idxs = np.array(data_norm.productId, dtype = np.int)

ratings = np.array(data_norm.scaled_purchase_freq)

n_customers = int(data_norm['customerId'].drop_duplicates().max()) + 1
n_products = int(data_norm['productId'].drop_duplicates().max()) + 1
n_factors = 50

input_shape = (1,)

print(n_customers)
print(n_products)
print(customer_idxs)
print(product_idxs)
print(ratings)


# ## 4.1 Tensorflow Session

# In[15]:


# create TF session and set it in Keras
sess = tf.Session()
K.set_session(sess)
K.set_learning_phase(1)


# ## 4.2 Model Class

# In[16]:


class DeepCollaborativeFiltering(Model):
    def __init__(self, n_customers, n_products, n_factors, p_dropout = 0.2):
        x1 = Input(shape = (1,), name="user")

        P = Embedding(n_customers, n_factors, input_length = 1)(x1)
        P = Reshape((n_factors,))(P)

        x2 = Input(shape = (1,), name="product")

        Q = Embedding(n_products, n_factors, input_length = 1)(x2)
        Q = Reshape((n_factors,))(Q)

        x = concatenate([P, Q], axis=1)
        x = Dropout(p_dropout)(x)

        x = Dense(n_factors)(x)
        x = Activation('relu')(x)
        x = Dropout(p_dropout)(x)

        output = Dense(1)(x)       
        
        super(DeepCollaborativeFiltering, self).__init__([x1, x2], output)
    
    def rate(self, customer_idxs, product_idxs):
        if (type(customer_idxs) == int and type(product_idxs) == int):
            return self.predict([np.array(customer_idxs).reshape((1,)), np.array(product_idxs).reshape((1,))])
        
        if (type(customer_idxs) == str and type(product_idxs) == str):
            return self.predict([np.array(customerMapping[customer_idxs]).reshape((1,)), np.array(productMapping[product_idxs]).reshape((1,))])
        
        return self.predict([
            np.array([customerMapping[customer_idx] for customer_idx in customer_idxs]), 
            np.array([productMapping[product_idx] for product_idx in product_idxs])
        ])


# ## 4.3 Hyperparameters

# In[17]:


bs = 64
val_per = 0.25
epochs = 3


# ## 4.4 Model Definition

# In[18]:


model = DeepCollaborativeFiltering(n_customers, n_products, n_factors)
model.summary()


# # 5 Training

# In[19]:


model.compile(optimizer = 'adam', loss = mean_squared_logarithmic_error)
model.fit(x = [customer_idxs, product_idxs], y = ratings, batch_size = bs, epochs = epochs, validation_split = val_per)
print('Done training!')


# ## 5.1 Log model and metrics

# In[20]:


logmodel = exec.log_output(
    metadata.Model(
            name="DeepCollaborativeFiltering",
            description="Model for product recommender",
            uri="",
            model_type="neural network",
            version=execTime,
            training_framework={
                "name": "tensorflow",
                "version": "v1.14"
            },
            hyperparameters={
                "batch_size" : 64,
                "validation_split" : 0.25,
                "layers": [n_customers, n_products, n_factors],
                "epochs" : 3
            }))
metrics = exec.log_output(
    metadata.Metrics(
            name="Model for product recommender evaluation",
            description="Validating of the recommender model",
            uri="",
            version=execTime,
            data_set_id=data_set.id,
            model_id=logmodel.id))


# # 6 Get current output directory for model

# In[21]:


directorystream = minioClient.get_object('data', 'recommender/directory.txt')
directory = ""
for d in directorystream.stream(32*1024):
    directory += d.decode('utf-8')
arg_version = "1"    
export_path = 's3://models/' + directory + '/' + arg_version + '/'
print ('Exporting trained model to', export_path)


# ## 6.1 Export models

# In[22]:


# inputs/outputs
tensor_info_users = tf.saved_model.utils.build_tensor_info(model.input[0])
tensor_info_products = tf.saved_model.utils.build_tensor_info(model.input[1])
tensor_info_pred = tf.saved_model.utils.build_tensor_info(model.output)

print ("tensor_info_users", tensor_info_users.name)
print ("tensor_info_products", tensor_info_products.name)
print ("tensor_info_pred", tensor_info_pred.name)


# In[23]:


# signature
prediction_signature = (tf.saved_model.signature_def_utils.build_signature_def(
        inputs={"users": tensor_info_users, "products": tensor_info_products},
        outputs={"predictions": tensor_info_pred},
        method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))
# export
legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
builder = tf.saved_model.builder.SavedModelBuilder(export_path)
builder.add_meta_graph_and_variables(
      sess, [tf.saved_model.tag_constants.SERVING],
      signature_def_map={
           tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
      },
      legacy_init_op=legacy_init_op)
builder.save()


# # 7 Restarting of the model serving server
# 
# In order for a new model to take effect it is also necessary to restart a model server.
# The issue here is that we are not changing the model version version and as a result, 
# the model will not be updated. To ensure model update, we are here restarting a server -
# simply killing the running instance, and as a server is installed using deployment, the instance
# will be recreated. Additionally for pods operations to work correctly from the notebook,
# it is necessary to create permissions allowing for access to pods in another namespace. 
# Look at the podaccessroles.yaml for details.

# In[24]:


recommender = "recommendermodelserver-"
if directory == "recommender1":
    recommender = "recommendermodelserver1-"
print("pod prefix ", recommender) 

namespace = "kubeflow"
print("pod namespace ", namespace) 


# In[26]:


# Get full pod name for the current model

k8s_config.load_incluster_config()

v1 = k8s_client.CoreV1Api()

pod_list = v1.list_namespaced_pod(namespace)
pod = [item.metadata.name for item in pod_list.items if recommender in item.metadata.name][0]
print("Current pod name ", pod)


# In[27]:


# Delete pod, so that it gets recreated
v1.delete_namespaced_pod(pod, namespace, grace_period_seconds=0)

print("Done deleting")


# In[28]:


# Verify that the new instance was created
time.sleep(20)
pod_list = v1.list_namespaced_pod(namespace)
pod = [item.metadata.name for item in pod_list.items if recommender in item.metadata.name][0]
print("New pod name ", pod)


# In[ ]:




