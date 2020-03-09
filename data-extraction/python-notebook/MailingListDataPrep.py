#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install lxml')
get_ipython().system('pip install git+https://github.com/kubernetes-client/python.git')


# In[2]:


from datetime import datetime
from requests import get
from lxml import etree
from time import sleep

import re

import pandas as pd


# In[ ]:


def scrapeMailArchives(mailingList: str, year: int, month: int):
    baseUrl = "http://mail-archives.apache.org/mod_mbox/%s/%s.mbox/ajax/" % (mailingList, datetime(year,month,1).strftime("%Y%m"))
    r = get(baseUrl + "thread?0")
    utf8_parser = etree.XMLParser(encoding='utf-8')
    root = etree.fromstring(r.text.replace('encoding="UTF-8"', ""),  parser=utf8_parser)
    output = []
    for message in root.xpath("//message"):
        _id = message.get("id")
        linked = message.get("linked")
        depth = message.get("depth")
        fr = message.xpath("from")[0].text
        dt = message.xpath("date")[0].text ## todo convert to date
        subject = message.xpath("subject")[0].text
        r2 = get(baseUrl + _id)
        bodyRoot = etree.fromstring(r2.text.replace('encoding="UTF-8"', ""),  parser=utf8_parser)
        body = bodyRoot.xpath("//contents")[0].text
        record = {
            "id"        : _id,
            "linked"    : linked,
            "depth"     : depth,
            "from"      : fr,
            "dt"        : dt,
            "subject"   : subject,
            "body"      : body
        }
        output.append(record)
        sleep(0.1)
    return output


def extract_links(body):
    link_regex_str = r'(http(|s)://(.*?))([\s\n]|$)'
    itr = re.finditer(link_regex_str, body, re.MULTILINE)
    return list(map(lambda elem: elem.group(1), itr))

def extract_domains(links):
    from urllib.parse import urlparse
    def extract_domain(link):
        try:
            nloc = urlparse(link).netloc
            # We want to drop www and any extra spaces wtf nloc on the spaces.
            regex_str = r'^(www\.|)(.*?)\s*$'
            match = re.search(regex_str, nloc)
            return match.group(2)
        except:
            return None
    return list(map(extract_domain, links))

def contains_python_stack_trace(body):
    return "Traceback (most recent call last)" in body

def contains_probably_java_stack_trace(body):
    # Look for something based on regex
    # Tried https://stackoverflow.com/questions/20609134/regular-expression-optional-multiline-java-stacktrace - more msg looking
    # Tried https://stackoverflow.com/questions/3814327/regular-expression-to-parse-a-log-file-and-find-stacktraces
    # Yes the compile is per call, but it's cached so w/e
    import re
    stack_regex_str = r'^\s*(.+Exception.*):\n(.*\n){0,3}?(\s+at\s+.*\(.*\))+'
    match = re.search(stack_regex_str, body, re.MULTILINE)
    return match is not None

def contains_exception_in_task(body):
    # Look for a line along the lines of ERROR Executor: Exception in task
    return "ERROR Executor: Exception in task" in body


# In[ ]:


datesToScrape =  [(2019, i) for i in range(1,10)] # + \
#                 [(2018, i) for i in range(1,13)] + \
#                 [(2017, i) for i in range(1,13)] + 

records = []
## todo, go back further
for y,m in datesToScrape:
    print(m,"-",y)
    records += scrapeMailArchives("spark-dev", y, m)


# In[ ]:


df = pd.DataFrame(records)
df['links'] = df['body'].apply(extract_links)
df['containsPythonStackTrace'] = df['body'].apply(contains_python_stack_trace)
df['containsJavaStackTrace'] = df['body'].apply(contains_probably_java_stack_trace)
df['containsExceptionInTaskBody'] = df['body'].apply(contains_exception_in_task)

df['domains'] = df['links'].apply(extract_domains)
df['isThreadStart'] = df['depth'] == '0'


# In[ ]:


from sklearn.feature_extraction.text import TfidfVectorizer

bodyV = TfidfVectorizer()
# bodyV = TfidfVectorizer(max_features=10000) #if we cared about making this 1:1 w holden's code.
bodyFeatures = bodyV.fit_transform(df['body'])

domainV = TfidfVectorizer()
# domainV = TfidfVectorizer(max_features=100)

## A couple of "None" domains really screwed the pooch on this one. Also, no lists just space seperated domains.
def makeDomainsAList(d):
    return ' '.join([a for a in d if not a is None])

domainFeatures = domainV.fit_transform(df['domains'].apply(makeDomainsAList))


# In[ ]:





# In[ ]:



from scipy.sparse import csr_matrix, hstack

data = hstack([csr_matrix(df[['containsPythonStackTrace', 'containsJavaStackTrace', 'containsExceptionInTaskBody', 'isThreadStart']].to_numpy()),
                             bodyFeatures,
                            domainFeatures])


from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

train, test = train_test_split(data, test_size=0.1)

kmeans = KMeans(n_clusters=2, random_state=42).fit(train)
train_pred = kmeans.predict(train)
test_pred = kmeans.predict(test)


# ### Now let's build some Pipelines!
# 
# Rawkintrevo is a rawkin dummy so check this link early and often: 
# https://www.kubeflow.org/docs/pipelines/sdk/sdk-overview/#standard-component-in-app
# 
# When I'm learning something new, I like to start with the dead simple example first and then "build it up" from there.  When it comes to composing Pipelines with Python, the dead simplest route are "Lightweight Python Functions" (link), and the dead simplest function is an echo. So here we're going to make our "Hello World" which is actually a numerical echo pipeline. That is to say, you put a number in, it spits the number out.
# 
# Let's start by importing `kfp` and defining our function.

# In[ ]:


get_ipython().system("pip3 install 'kfp' ")


# In[3]:


import kfp

def deadSimpleIntEchoFn(i: int) -> int:
    return i


# OK, nothing too crazy there, amirigh? Notice we typed everything. You don't _have_ to as far as I know, but really that's just good practice. Many a bug have been introduced by not strongly typing variables. I'm sure some Python-ados are cussing up a storm right now, and to them I say- go back to R, the adults are talking over here. 
# 
# Next step, we want to wrap our function `deadSimpleIntEchoFn` into a Kubeflow Pipelin Operation.  There's a nice little method to do this called `kfp.components.func_to_container_op`. This will return a factory function with a strongly typed signature. 
# 

# In[4]:


simpleStronglyTypedFunction = kfp.components.func_to_container_op(deadSimpleIntEchoFn)


# When we create a pipeline in the next step, the factory will construct a `ContainerOp`, which will run the original function (`deadSimpleIntEchoFn`) in a container. To prove that, check this out:

# In[5]:


foo = simpleStronglyTypedFunction(1)
type(foo)


# OK, I know that seems trivial, I myself am nearly bored to tears. But this will be important when we start trying to mount data volumes (of y'know, training data, and other stuff), in the second merry-go-round.
# 
# For now, let's finish off this patronizingly simple example by defining and compiling our Pipeline.

# In[6]:


@kfp.dsl.pipeline(
  name='Dead Simple 1',
  description='This is for all intents and purposes and echo pipeline. We take a number in, we spit it back out.'
)
def echo_pipeline(param_1: kfp.dsl.PipelineParam):
  my_step = simpleStronglyTypedFunction(i= param_1)

kfp.compiler.Compiler().compile(echo_pipeline,  
  'echo-pipeline.zip')


# OK, now to run this pipeline, you can go one of two ways. You can run it via code, or you can download `echo-pipeline.zip` go over to the Pipelines WebUI, upload it, do experiments, etc. I get paid by the page over here, so guess which one I'm going to take screen shots of? 
# 
# [Screenshots of rt click / download / uplaod ]
# 
# Jk, in the next example I'll show how to execute it with code too, but it's not nearly as pretty. I feel like people making these back end tools really never spend enough time on making the WebUI look good. Two notable exceptions are Apache Flink, and Kubeflow. 

# ### A slightly less dead simple example
# 
# In this we're going ot pull down some data from the internet.  IRL you would probably want to connect to a database or a stream or whatever the cool kids are doing by the time you read this. 
# 
# First we'll declare our data fetching algorithm, which takes an Apache Email List, and a year and will get first a list of all the messages, then iterarte through and download each message. Note two things- it will get at MOST one year of data, and it sleeps in between calls. Don't be a jerk- if you want to try something on bigger data, got get your own set, the Apache Software Foundation is a charity- so don't abuse their mail archives just because. 

# In[102]:


def download_data() -> bool:
    ## packages_to_install should cover this, but seems to be missing? so we have to hack
    from pip._internal import main as pipmain
    pipmain(['install', 'lxml', 'requests'])
    
    # / hacks
    
    from datetime import datetime
    from lxml import etree
    from requests import get
    from time import sleep
    
    import json
    
    def scrapeMailArchives(mailingList: str, year: int, month: int):
        baseUrl = "http://mail-archives.apache.org/mod_mbox/%s/%s.mbox/ajax/" % (mailingList, datetime(year,month,1).strftime("%Y%m"))
        r = get(baseUrl + "thread?0")
        utf8_parser = etree.XMLParser(encoding='utf-8')
        root = etree.fromstring(r.text.replace('encoding="UTF-8"', ""),  parser=utf8_parser)
        output = []
        for message in root.xpath("//message"):
            _id = message.get("id")
            linked = message.get("linked")
            depth = message.get("depth")
            fr = message.xpath("from")[0].text
            dt = message.xpath("date")[0].text ## todo convert to date
            subject = message.xpath("subject")[0].text
            r2 = get(baseUrl + _id)
            bodyRoot = etree.fromstring(r2.text.replace('encoding="UTF-8"', ""),  parser=utf8_parser)
            body = bodyRoot.xpath("//contents")[0].text
            record = {
                "id"        : _id,
                "linked"    : linked,
                "depth"     : depth,
                "from"      : fr,
                "dt"        : dt,
                "subject"   : subject,
                "body"      : body
            }
            output.append(record)
            sleep(0.1)
            
        return output

    datesToScrape =  [(2019, i) for i in range(1,2)] # + \
    #                 [(2018, i) for i in range(1,13)] + \
    #                 [(2017, i) for i in range(1,13)] + 

    records = []
    ## todo, go back further
    for y,m in datesToScrape:
        print(m,"-",y)
        records += scrapeMailArchives("spark-dev", y, m)
    import os
    output_path = '/data_processing/data.json'
    with open(output_path, 'w') as f:
        json.dump(records, f)
    
    return True
    


# ### Doing Witchcraft
# 
# Remember earlier when we did that big (and arguably pointless) classification of emails from the Apache Spark mailing list? OK, now we're going to do it again, as a "lightweight" Python function in a Kubeflow Pipeline.  I hope the irony of the term "lightweight" isn't lost on anyone, because this is pretty blatent abuse of something that was originally presented for conveinience. 
# 
# First note, all of the imports and declarations of helper functions MUST be with in the "ligthweight" function.  This train wreck even has me upgrading `pandas`.  One could argue (and they would probably be correct) that I have two steps here- feature prep and ML, and as such I should split them. I would say that's fair, but I choose not to do so at this time.  Perhaps in some scripts later on?
# 
# As has been pointed out so many times before, we assume the reader either arleady understands what is going on with the KMeans clustering, or better yet, doesn't even care. I won't be digging into that right now. What I will point out- and maybe as a note to the editor, the model that is finally saved really ought to be persisted somewhere.  If the model isn't saved, then this basically pointless pipeline, is truly pointless. 
# 

# Now let's make sure we can read that data in the next step (before we write a big complicated model to do whatever torture to it).

# In[120]:


def do_witchcraft(fn_input: bool):
    
    from pip._internal import main as pipmain
    pipmain(['install', '--upgrade', 'pandas']) # df.to_numpy is new in 0.24 which isolder than whatever is shipped here
    
    import json
    import re
    import pandas as pd
    
    print("loading records...")
    with open('/data_processing/data.json', 'r') as f:
        records = json.load(f)
    print("records loaded")
    
    
    ## Note: "Lightweight" Python Fns mean helper code must be inside the fn. (Bad Form)
    def extract_links(body):
        link_regex_str = r'(http(|s)://(.*?))([\s\n]|$)'
        itr = re.finditer(link_regex_str, body, re.MULTILINE)
        return list(map(lambda elem: elem.group(1), itr))

    def extract_domains(links):
        from urllib.parse import urlparse
        def extract_domain(link):
            try:
                nloc = urlparse(link).netloc
                # We want to drop www and any extra spaces wtf nloc on the spaces.
                regex_str = r'^(www\.|)(.*?)\s*$'
                match = re.search(regex_str, nloc)
                return match.group(2)
            except:
                return None
        return list(map(extract_domain, links))

    def contains_python_stack_trace(body):
        return "Traceback (most recent call last)" in body

    def contains_probably_java_stack_trace(body):
        # Look for something based on regex
        # Tried https://stackoverflow.com/questions/20609134/regular-expression-optional-multiline-java-stacktrace - more msg looking
        # Tried https://stackoverflow.com/questions/3814327/regular-expression-to-parse-a-log-file-and-find-stacktraces
        # Yes the compile is per call, but it's cached so w/e
        import re
        stack_regex_str = r'^\s*(.+Exception.*):\n(.*\n){0,3}?(\s+at\s+.*\(.*\))+'
        match = re.search(stack_regex_str, body, re.MULTILINE)
        return match is not None

    def contains_exception_in_task(body):
        # Look for a line along the lines of ERROR Executor: Exception in task
        return "ERROR Executor: Exception in task" in body
    
    df = pd.DataFrame(records)
    print(df.shape)
    df['links'] = df['body'].apply(extract_links)
    df['containsPythonStackTrace'] = df['body'].apply(contains_python_stack_trace)
    df['containsJavaStackTrace'] = df['body'].apply(contains_probably_java_stack_trace)
    df['containsExceptionInTaskBody'] = df['body'].apply(contains_exception_in_task)

    df['domains'] = df['links'].apply(extract_domains)
    df['isThreadStart'] = df['depth'] == '0'
    
    # Arguably, you could split building the dataset away from the actual witchcraft.
    from sklearn.feature_extraction.text import TfidfVectorizer

    bodyV = TfidfVectorizer()
    # bodyV = TfidfVectorizer(max_features=10000) #if we cared about making this 1:1 w holden's code.
    bodyFeatures = bodyV.fit_transform(df['body'])

    domainV = TfidfVectorizer()
    # domainV = TfidfVectorizer(max_features=100)

    ## A couple of "None" domains really screwed the pooch on this one. Also, no lists just space seperated domains.
    def makeDomainsAList(d):
        return ' '.join([a for a in d if not a is None])

    domainFeatures = domainV.fit_transform(df['domains'].apply(makeDomainsAList))

    from scipy.sparse import csr_matrix, hstack

    data = hstack([csr_matrix(df[['containsPythonStackTrace', 'containsJavaStackTrace', 'containsExceptionInTaskBody', 'isThreadStart']].to_numpy()),
                                 bodyFeatures,
                                domainFeatures])


    from sklearn.cluster import KMeans
    from sklearn.model_selection import train_test_split

    train, test = train_test_split(data, test_size=0.1)

    kmeans = KMeans(n_clusters=2, random_state=42).fit(train)
    train_pred = kmeans.predict(train)
    test_pred = kmeans.predict(test)
    print(test_pred)
    # TODO: Dump the model somewhere you can use it later. 


# 
# ### The Kubeflow Bit.
# 
# OK, now you've seen a fairly exhuastive demonstration of antipatterns in programming, let's get down to the business of this book and actually create our Kubeflow Pipeline.  First you will notice we have to call in `k8s_client`.  My version of (working) Kubeflow is old and uses a somewhat antiquated method for attatching volumes to `ContainerOps`.  You should recall `ContainrOps` from the previous chapter, but here I will say, they are actually created not at 
# ```
# witchcraft_fn =...
# ```
# 
# But at 
# ```
# step1 = ...
# step2 = ...
# ```
# 
# Which is why it is there, we are adding the `add_volume` and `add_volume_mount`. 
# 
# Obviously PVCs are only one of many ways to get data into our containers, and honestly may not be the _best_ way.  However, we often may "get" our data in the first step and then need to hand it, in various stages, from one component to the next, and in these cases, `PersistentVolumeClaims` work exceedingly well, and so they are presented as an example. 
# 
# 

# In[122]:


from kubernetes import client as k8s_client

download_data_fn = kfp.components.func_to_container_op(download_data)
witchcraft_fn = kfp.components.func_to_container_op(do_witchcraft)

@kfp.dsl.pipeline(
  name='Simple1',
  description='Simple1'
)
def my_pipeline2():
    ## Note this is OLD code, cleaner way to do it now- revisit when you have 0.7 up
    step1 = download_data_fn().add_volume(k8s_client.V1Volume(name='data-processing',
                                                                                  host_path=k8s_client.V1HostPathVolumeSource(path='/data_processing'))) \
                            .add_volume_mount(k8s_client.V1VolumeMount(
                                          mount_path='/data_processing',
                                          name='data-processing'))
    step2 = witchcraft_fn(fn_input= step1.output).add_volume(k8s_client.V1Volume(name='data-processing',
                                                                                  host_path=k8s_client.V1HostPathVolumeSource(path='/data_processing'))) \
                            .add_volume_mount(k8s_client.V1VolumeMount(
                                          mount_path='/data_processing',
                                          name='data-processing'))

kfp.compiler.Compiler().compile(my_pipeline2, 'my-pipeline6.zip')


# And just like that, we've done it. We've created a Kubeflow Pipeline.
# 
# So let's take a moment to step back and think, "what in the crazy-town-heck is going on here?!".  A valid question, and well spotted.  Each "Step" is going to be creating a container.  Maybe I should have noted that earlier when talking about attatching volumes, beacuse if you thougth I was doing that to a function, you'd probably think me quite insane. 
# 
# But, if you follow this code, and create this pipeline, download it and run it, you will see each "step" as a seperate container, downloading data, saving it to a `PVC` then passing some parameters to a next container, which also will load the `PVC`, etc. etc.  
# 
# ### Using Python to Create Containers, but not like a crazy person
# 
# For completeness, let's last explore how to do all of these things like not a psycopath. 
# 
# The trick for the most part is to create a function that returns a `kfp.dsl.ContainerOp`.  This will point to an image, note the volumes that need to be mounted, and a number of other things. I've heard told people don't always just like creating absurdly large and fat functions to do everything in real life, so I leave this hear as an aside in case the reader is interested in it.  It's alsow worth noting that adding the `@kfp.dsl.component` annotation instructs teh Kubeflow compiler to turn on static typce checking. 
# 
# ```
# @kfp.dsl.component
# def my_component(my_param):
#   ...
#   return kfp.dsl.ContainerOp(
#     name='My component name',
#     image='gcr.io/path/to/container/image'
#   )
# ```
# 
# Finally, when it comes to incorporating these components into pipelines, you would do something like this:
# 
# ```
# @kfp.dsl.pipeline(
#   name='My pipeline',
#   description='My machine learning pipeline'
# )
# def my_pipeline(param_1: PipelineParam, param_2: PipelineParam):
#   my_step = my_component(my_param='a')
# ```
# 
# Which should look exceedingly familiar as we did something very similar with our `download_data_fn` and `witchcraft_fn`.  

# In[ ]:




