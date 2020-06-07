#!/usr/bin/env python
# coding: utf-8

# # mlflow-energyforecast
#
# This is a showcase for ML Flow capabilities, based on the article
# http://the-odd-dataguy.com/be-more-efficient-to-produce-ml-models-with-mlflow
# and a github https://github.com/jeanmidevacc/mlflow-energyforecast
#

# In[2]:

get_ipython().system('pip install pandas --upgrade --user')
get_ipython().system('pip install mlflow --upgrade --user')
get_ipython().system('pip install joblib --upgrade --user')
get_ipython().system('pip install numpy --upgrade --user ')
get_ipython().system('pip install scipy --upgrade --user ')
get_ipython().system('pip install scikit-learn --upgrade --user')
get_ipython().system('pip install boto3 --upgrade --user')

# In[3]:

import time
import json
import os
from joblib import Parallel, delayed

import pandas as pd
import numpy as np
import scipy

from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
from sklearn.exceptions import ConvergenceWarning

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=ConvergenceWarning)

# In[4]:

# Ensure Minio access
os.environ[
    'MLFLOW_S3_ENDPOINT_URL'] = 'http://minio-service.kubeflow.svc.cluster.local:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'

# # Data preparation

# In[5]:

# Collect the data
df_nationalconsumption_electricity_daily = pd.read_csv(
    "https://raw.githubusercontent.com/jeanmidevacc/mlflow-energyforecast/master/data/rtu_data.csv"
)
df_nationalconsumption_electricity_daily.set_index(["day"], inplace=True)

# In[6]:

# Prepare the training set and the testing set
df_trainvalidate_energyconsumption = df_nationalconsumption_electricity_daily[
    df_nationalconsumption_electricity_daily["datastatus"] == "Définitif"]
del df_trainvalidate_energyconsumption["datastatus"]

df_test_energyconsumption = df_nationalconsumption_electricity_daily[
    df_nationalconsumption_electricity_daily["datastatus"] == "Consolidé"]
del df_test_energyconsumption["datastatus"]

print("Size of the training set : ", len(df_trainvalidate_energyconsumption))
print("Size of the testing set : ", len(df_test_energyconsumption))

# In[7]:

# Define the inputs and the output
output = "dailyconsumption"
allinputs = list(df_trainvalidate_energyconsumption.columns)
allinputs.remove(output)

print("Output to predict : ", output)
print("Inputs for the prediction : ", allinputs)

# In[8]:

# Build different set of featurws for the model
possible_inputs = {
    "all":
    allinputs,
    "only_allday_inputs": ["weekday", "month", "is_holiday", "week"],
    "only_allweatheravg_inputs": [
        "avg_min_temperature", "avg_max_temperature", "avg_mean_temperature",
        "wavg_min_temperature", "wavg_max_temperature", "wavg_mean_temperature"
    ],
    "only_meanweather_inputs_avg": ["avg_mean_temperature"],
    "only_meanweather_inputs_wavg": ["wavg_mean_temperature"],
}

# In[9]:

# Prepare the output of the model
array_output_train = np.array(df_trainvalidate_energyconsumption[output])
array_output_test = np.array(df_test_energyconsumption[output])

# In[10]:

# connect to remote server
remote_server_uri = "http://mlflowserver.kubeflow.svc.cluster.local:5000"
mlflow.set_tracking_uri(remote_server_uri)
# Launch the experiment on mlflow
experiment_name = "electricityconsumption-forecast"
mlflow.set_experiment(experiment_name)

# In[11]:


# Define the evaluation function that will do the computation of the different metrics of accuracy (RMSE,MAE,R2)
def evaluation_model(y_test, y_pred):

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    metrics = {
        "rmse": rmse,
        "r2": r2,
        "mae": mae,
    }

    return metrics


# # KNN regressor

# In[12]:

from sklearn.neighbors import KNeighborsRegressor


def train_knnmodel(parameters, inputs, tags, log=False):
    with mlflow.start_run(nested=True):

        # Prepare the data
        array_inputs_train = np.array(
            df_trainvalidate_energyconsumption[inputs])
        array_inputs_test = np.array(df_test_energyconsumption[inputs])

        # Build the model
        tic = time.time()
        model = KNeighborsRegressor(parameters["nbr_neighbors"],
                                    weights=parameters["weight_method"])
        model.fit(array_inputs_train, array_output_train)
        duration_training = time.time() - tic

        # Make the prediction
        tic1 = time.time()
        prediction = model.predict(array_inputs_test)
        duration_prediction = time.time() - tic1

        # Evaluate the model prediction
        metrics = evaluation_model(array_output_test, prediction)

        # Log in the console
        if log:
            print(f"KNN regressor:")
            print(parameters)
            print(metrics)

        # Log in mlflow (parameter)
        mlflow.log_params(parameters)

        # Log in mlflow (metrics)
        metrics["duration_training"] = duration_training
        metrics["duration_prediction"] = duration_prediction
        mlflow.log_metrics(metrics)

        # log in mlflow (model)
        mlflow.sklearn.log_model(model, f"model")

        # Tag the model
        mlflow.set_tags(tags)


# In[13]:

# Test the different combinations
configurations = []
for nbr_neighbors in [1, 2, 5, 10]:
    for weight_method in ['uniform', 'distance']:
        for field in possible_inputs:
            parameters = {
                "nbr_neighbors": nbr_neighbors,
                "weight_method": weight_method
            }

            tags = {"model": "knn", "inputs": field}

            configurations.append([parameters, tags])

            train_knnmodel(parameters, possible_inputs[field], tags)

# # MLP regressor

# In[14]:

from sklearn.neural_network import MLPRegressor


def train_mlpmodel(parameters, inputs, tags, log=False):
    with mlflow.start_run(nested=True):

        # Prepare the data
        array_inputs_train = np.array(
            df_trainvalidate_energyconsumption[inputs])
        array_inputs_test = np.array(df_test_energyconsumption[inputs])

        # Build the model
        tic = time.time()

        model = MLPRegressor(hidden_layer_sizes=parameters["hidden_layers"],
                             activation=parameters["activation"],
                             solver=parameters["solver"],
                             max_iter=parameters["nbr_iteration"],
                             random_state=0)

        model.fit(array_inputs_train, array_output_train)
        duration_training = time.time() - tic

        # Make the prediction
        tic1 = time.time()
        prediction = model.predict(array_inputs_test)
        duration_prediction = time.time() - tic1

        # Evaluate the model prediction
        metrics = evaluation_model(array_output_test, prediction)

        # Log in the console
        if log:
            print(f"Random forest regressor:")
            print(parameters)
            print(metrics)

        # Log in mlflow (parameter)
        mlflow.log_params(parameters)

        # Log in mlflow (metrics)
        metrics["duration_training"] = duration_training
        metrics["duration_prediction"] = duration_prediction
        mlflow.log_metrics(metrics)

        # log in mlflow (model)
        mlflow.sklearn.log_model(model, f"model")

        # Tag the model
        mlflow.set_tags(tags)


# In[15]:

for hiddenlayers in [4, 8, 16]:
    for activation in [
            "identity",
            "logistic",
    ]:
        for solver in ["lbfgs"]:
            for nbriteration in [10, 100, 1000]:
                for field in possible_inputs:
                    parameters = {
                        "hidden_layers": hiddenlayers,
                        "activation": activation,
                        "solver": solver,
                        "nbr_iteration": nbriteration
                    }

                    tags = {"model": "mlp", "inputs": field}

                    train_mlpmodel(parameters, possible_inputs[field], tags)

# # Use a handmade model (scipy approach)

# In[16]:


class PTG:
    def __init__(self, thresholds_x0, thresholds_a, thresholds_b):
        self.thresholds_x0 = thresholds_x0
        self.thresholds_a = thresholds_a
        self.thresholds_b = thresholds_b

    def get_ptgmodel(self, x, a, b, x0):
        return np.piecewise(x, [x < x0, x >= x0],
                            [lambda x: a * x + b, lambda x: a * x0 + b])

    def fit(self, dfx, y):
        x = np.array(dfx)

        # Define the bounds
        bounds_min = [thresholds_a[0], thresholds_b[0], thresholds_x0[0]]
        bounds_max = [thresholds_a[1], thresholds_b[1], thresholds_x0[1]]
        bounds = (bounds_min, bounds_max)

        # Fit a model
        popt, pcov = scipy.optimize.curve_fit(self.get_ptgmodel,
                                              x,
                                              y,
                                              bounds=bounds)

        # Get the parameter of the model
        a = popt[0]
        b = popt[1]
        x0 = popt[2]

        self.coefficients = [a, b, x0]

    def predict(self, dfx):
        x = np.array(dfx)
        predictions = []
        for elt in x:
            forecast = self.get_ptgmodel(elt, self.coefficients[0],
                                         self.coefficients[1],
                                         self.coefficients[2])
            predictions.append(forecast)
        return np.array(predictions)


def train_ptgmodel(parameters, inputs, tags, log=False):
    with mlflow.start_run(nested=True):

        # Prepare the data
        df_inputs_train = df_trainvalidate_energyconsumption[inputs[0]]
        df_inputs_test = df_test_energyconsumption[inputs[0]]

        # Build the model
        tic = time.time()

        model = PTG(parameters["thresholds_x0"], parameters["thresholds_a"],
                    parameters["thresholds_b"])

        model.fit(df_inputs_train, array_output_train)
        duration_training = time.time() - tic

        # Make the prediction
        tic1 = time.time()
        prediction = model.predict(df_inputs_test)
        duration_prediction = time.time() - tic1

        # Evaluate the model prediction
        metrics = evaluation_model(array_output_test, prediction)

        # Log in the console
        if log:
            print(f"PTG:")
            print(parameters)
            print(metrics)

        # Log in mlflow (parameter)
        mlflow.log_params(parameters)

        # Log in mlflow (metrics)
        metrics["duration_training"] = duration_training
        metrics["duration_prediction"] = duration_prediction
        mlflow.log_metrics(metrics)

        # log in mlflow (model)
        mlflow.sklearn.log_model(model, f"model")

        # Tag the model
        mlflow.set_tags(tags)


# In[17]:

# Define the parameters of the model
thresholds_x0 = [0, 20]
thresholds_a = [-200000, -50000]
thresholds_b = [1000000, 3000000]

parameters = {
    "thresholds_x0": thresholds_x0,
    "thresholds_a": thresholds_a,
    "thresholds_b": thresholds_b
}

for field in ["only_meanweather_inputs_avg", "only_meanweather_inputs_wavg"]:

    tags = {"model": "ptg", "inputs": field}

    train_ptgmodel(parameters, possible_inputs[field], tags, log=False)

# # Evaluate mlflow results

# In[18]:

# Select the run of the experiment
df_runs = mlflow.search_runs(experiment_ids="0")
print("Number of runs done : ", len(df_runs))

# In[19]:

# Quick sorting to get the best models based on the RMSE metric
df_runs.sort_values(["metrics.rmse"], ascending=True, inplace=True)
df_runs.head()

# In[20]:

# Get the best one
runid_selected = df_runs.head(1)["run_id"].values[0]
runid_selected

# In[ ]:
