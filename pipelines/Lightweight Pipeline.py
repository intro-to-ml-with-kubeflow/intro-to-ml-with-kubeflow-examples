#!/usr/bin/env python
# coding: utf-8

# # Setup

# In[1]:


get_ipython().system('pip install kfp --upgrade --user')

import kfp 
from kfp import compiler
import kfp.dsl as dsl
import kfp.notebook
import kfp.components as comp


# Simple function that just add two numbers:

# In[2]:


#Define a Python function
def add(a: float, b: float) -> float:
   '''Calculates sum of two arguments'''
   return a + b


# Convert the function to a pipeline operation

# In[3]:


add_op = comp.func_to_container_op(add)


# A bit more advanced function which demonstrates how to use imports, helper functions and produce multiple outputs.

# In[4]:


from typing import NamedTuple
def my_divmod(dividend: float, divisor:float) -> NamedTuple('MyDivmodOutput', [('quotient', float), ('remainder', float)]):
    '''Divides two numbers and calculate  the quotient and remainder'''
    #Imports inside a component function:
    import numpy as np

    #This function demonstrates how to use nested functions inside a component function:
    def divmod_helper(dividend, divisor):
        return np.divmod(dividend, divisor)

    (quotient, remainder) = divmod_helper(dividend, divisor)

    from collections import namedtuple
    divmod_output = namedtuple('MyDivmodOutput', ['quotient', 'remainder'])
    return divmod_output(quotient, remainder)


# Test running the python function directly

# In[5]:


my_divmod(100, 7)


# Convert the function to a pipeline operation

# In[6]:


divmod_op = comp.func_to_container_op(my_divmod, base_image='tensorflow/tensorflow:1.14.0-py3')


# Define the pipeline
# Pipeline function has to be decorated with the @dsl.pipeline decorator

# In[7]:


@dsl.pipeline(
   name='Calculation pipeline',
   description='A toy pipeline that performs arithmetic calculations.'
)
def calc_pipeline(
   a='a',
   b='7',
   c='17',
):
    #Passing pipeline parameter and a constant value as operation arguments
    add_task = add_op(a, 4) #Returns a dsl.ContainerOp class instance. 
    
    #Passing a task output reference as operation arguments
    #For an operation with a single return value, the output reference can be accessed using `task.output` or `task.outputs['output_name']` syntax
    divmod_task = divmod_op(add_task.output, b)

    #For an operation with a multiple return values, the output references can be accessed using `task.outputs['output_name']` syntax
    result_task = add_op(divmod_task.outputs['quotient'], c)


# Submit the pipeline for execution

# In[8]:


client = kfp.Client()

#Specify pipeline argument values
arguments = {'a': '7', 'b': '8'}

#Submit a pipeline run
client.create_run_from_pipeline_func(calc_pipeline, arguments=arguments)


# In[ ]:




