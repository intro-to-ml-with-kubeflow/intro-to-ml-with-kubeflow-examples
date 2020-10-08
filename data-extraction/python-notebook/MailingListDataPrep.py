#!/usr/bin/env python
# coding: utf-8

# Here we can install some packages our notebook needs. We can also install them in our container to speed things up & make it more reliable. But for prototyping this works great!

# In[ ]:

get_ipython().system('pip3 install --upgrade lxml')
get_ipython().system('pip3 install --upgrade pandas')
get_ipython().system('pip3 install --upgrade scikit-learn')
get_ipython().system('pip3 install --upgrade scipy')
get_ipython().system('pip3 install --upgrade tables')

# We can use Jupyter notebooks just like normal inside of Kubeflow

# In[ ]:

from datetime import datetime
from requests import get
from lxml import etree
from time import sleep

import re

import pandas as pd

import os

# In[ ]:

container_registry = ""  # Wherever you put your containers

# In[ ]:


def scrapeMailArchives(mailingList: str, year: int, month: int):
    baseUrl = "http://mail-archives.apache.org/mod_mbox/%s/%s.mbox/ajax/" % (
        mailingList, datetime(year, month, 1).strftime("%Y%m"))
    r = get(baseUrl + "thread?0")
    utf8_parser = etree.XMLParser(encoding='utf-8')
    root = etree.fromstring(r.text.replace('encoding="UTF-8"', ""),
                            parser=utf8_parser)
    output = []
    for message in root.xpath("//message"):
        _id = message.get("id")
        linked = message.get("linked")
        depth = message.get("depth")
        fr = message.xpath("from")[0].text
        dt = message.xpath("date")[0].text  # todo convert to date
        subject = message.xpath("subject")[0].text
        r2 = get(baseUrl + _id)
        bodyRoot = etree.fromstring(r2.text.replace('encoding="UTF-8"', ""),
                                    parser=utf8_parser)
        body = bodyRoot.xpath("//contents")[0].text
        record = {
            "id": _id,
            "linked": linked,
            "depth": depth,
            "from": fr,
            "dt": dt,
            "subject": subject,
            "body": body
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

datesToScrape = [(2019, i) for i in range(1, 13)]

records = []
for y, m in datesToScrape:
    print(m, "-", y)
    records += scrapeMailArchives("spark-dev", y, m)

# In[ ]:

df = pd.DataFrame(records)
df['links'] = df['body'].apply(extract_links)
df['containsPythonStackTrace'] = df['body'].apply(contains_python_stack_trace)
df['containsJavaStackTrace'] = df['body'].apply(
    contains_probably_java_stack_trace)
df['containsExceptionInTaskBody'] = df['body'].apply(
    contains_exception_in_task)

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

data = hstack([
    csr_matrix(df[[
        'containsPythonStackTrace', 'containsJavaStackTrace',
        'containsExceptionInTaskBody', 'isThreadStart'
    ]].to_numpy()), bodyFeatures, domainFeatures
])

from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

train, test = train_test_split(data, test_size=0.1)

kmeans = KMeans(n_clusters=2, random_state=42).fit(train)
train_pred = kmeans.predict(train)
test_pred = kmeans.predict(test)

# Alternatively, by structuring our code correctly we can take advantage of pipelines

# In[ ]:

get_ipython().system('pip3 install --upgrade kfp')

# In[ ]:

import kfp
import kfp.dsl as dsl

# In[ ]:


def download_data(year: int) -> str:

    from datetime import datetime
    from lxml import etree
    from requests import get
    from time import sleep

    import json

    def scrapeMailArchives(mailingList: str, year: int, month: int):
        baseUrl = "http://mail-archives.apache.org/mod_mbox/%s/%s.mbox/ajax/" % (
            mailingList, datetime(year, month, 1).strftime("%Y%m"))
        r = get(baseUrl + "thread?0")
        utf8_parser = etree.XMLParser(encoding='utf-8')
        root = etree.fromstring(r.text.replace('encoding="UTF-8"', ""),
                                parser=utf8_parser)
        output = []
        for message in root.xpath("//message"):
            _id = message.get("id")
            linked = message.get("linked")
            depth = message.get("depth")
            fr = message.xpath("from")[0].text
            dt = message.xpath("date")[0].text  # todo convert to date
            subject = message.xpath("subject")[0].text
            r2 = get(baseUrl + _id)
            bodyRoot = etree.fromstring(r2.text.replace(
                'encoding="UTF-8"', ""),
                                        parser=utf8_parser)
            body = bodyRoot.xpath("//contents")[0].text
            record = {
                "id": _id,
                "linked": linked,
                "depth": depth,
                "from": fr,
                "dt": dt,
                "subject": subject,
                "body": body
            }
            output.append(record)
            sleep(0.1)

        return output

    datesToScrape = [(year, i) for i in range(1, 2)]

    records = []
    ## todo, go back further
    for y, m in datesToScrape:
        print(m, "-", y)
        records += scrapeMailArchives("spark-dev", y, m)
    import os
    output_path = '/data_processing/data.json'
    with open(output_path, 'w') as f:
        json.dump(records, f)

    return output_path


# In[ ]:

# In[ ]:


def download_tld_data() -> str:
    from requests import get
    import pandas as pd
    print("importing io....")
    import io

    url = "https://pkgstore.datahub.io/core/country-list/data_csv/data/d7c9d7cfb42cb69f4422dec222dbbaa8/data_csv.csv"
    print("Getting the url")
    s = get(url).content
    print("Converting content")
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    print("Writing output")
    output_path_hdf = '/tld_info/clean_data.hdf'
    df.to_hdf(output_path_hdf, key="tld")

    return output_path_hdf


# In[ ]:

# Now that we have some data, we want to get rid of any "bad" records

# In[ ]:


#tag::clean_data_fun[]
def clean_data(input_path: str) -> str:
    import json
    import pandas as pd

    print("loading records...")
    with open(input_path, 'r') as f:
        records = json.load(f)
    print("records loaded")

    df = pd.DataFrame(records)
    # Drop records without a subject, body, or sender
    cleaned = df.dropna(subset=["subject", "body", "from"])

    output_path_hdf = '/data_processing/clean_data.hdf'
    cleaned.to_hdf(output_path_hdf, key="clean")

    return output_path_hdf


#end::clean_data_fun[]

# ### Preparing the data
#
# Remember earlier when we did that big (and arguably pointless) classification of emails from the Apache Spark mailing list? OK, now we're going to do it again, as a "lightweight" Python function in a Kubeflow Pipeline.  I hope the irony of the term "lightweight" isn't lost on anyone, because this is pretty blatent abuse of something that was originally presented for conveinience.
#
# First note, all of the imports and declarations of helper functions MUST be with in the "ligthweight" function. One could argue (and they would probably be correct) that I have two steps here- feature prep and ML, and as such I should split them. I would say that's fair, but I choose not to do so at this time.  Perhaps in some scripts later on?
#
# As has been pointed out so many times before, we assume the reader either arleady understands what is going on with the KMeans clustering, or better yet, doesn't even care. I won't be digging into that right now. What I will point out- and maybe as a note to the editor, the model that is finally saved really ought to be persisted somewhere.  If the model isn't saved, then this basically pointless pipeline, is truly pointless.
#

# Now let's make sure we can read that data in the next step (before we write a big complicated model to do whatever torture to it).

# In[ ]:


def prepare_features(input_path: str, tld_info_path: str):

    import re
    import pandas as pd

    print("loading records...")
    df = pd.read_hdf(input_path, key="clean")
    print("records loaded")

    print("Loading tld info....")
    tld_df = pd.read_hdf(tld_info_path, key="tld")
    print("Loaded tld info")

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

    print(df.shape)
    df['links'] = df['body'].apply(extract_links)
    df['containsPythonStackTrace'] = df['body'].apply(
        contains_python_stack_trace)
    df['containsJavaStackTrace'] = df['body'].apply(
        contains_probably_java_stack_trace)
    df['containsExceptionInTaskBody'] = df['body'].apply(
        contains_exception_in_task)

    #tag::local_mailing_list_feature_prep_fun[]
    df['domains'] = df['links'].apply(extract_domains)
    df['isThreadStart'] = df['depth'] == '0'

    # Arguably, you could split building the dataset away from the actual witchcraft.
    from sklearn.feature_extraction.text import TfidfVectorizer

    bodyV = TfidfVectorizer()
    bodyFeatures = bodyV.fit_transform(df['body'])

    domainV = TfidfVectorizer()

    ## A couple of "None" domains really screwed the pooch on this one.Also, no lists just space seperated domains.
    def makeDomainsAList(d):
        return ' '.join([a for a in d if not a is None])

    domainFeatures = domainV.fit_transform(
        df['domains'].apply(makeDomainsAList))

    from scipy.sparse import csr_matrix, hstack

    data = hstack([
        csr_matrix(df[[
            'containsPythonStackTrace', 'containsJavaStackTrace',
            'containsExceptionInTaskBody', 'isThreadStart'
        ]].to_numpy()), bodyFeatures, domainFeatures
    ])
    #end::local_mailing_list_feature_prep_fun[]


#
# ### The Kubeflow Bit.
#
# Now we can put these two pieces together into a pipeline. Since the data is relatively small we will use a persistent volume put them together. Later on we can add training to this pipeline as well.
#
#

# In[ ]:

# Make a volume example. We redo it inside of the pipeline definition because we need to be inside
#tag::makeVolume[]
dvop = dsl.VolumeOp(name="create_pvc",
                    resource_name="my-pvc-2",
                    size="5Gi",
                    modes=dsl.VOLUME_MODE_RWO)
#end::makeVolume[]

# In[ ]:

get_ipython().system('rm local-data-prep-2.zip')

# In[ ]:


#tag::makePipeline[]
@kfp.dsl.pipeline(name='Simple1', description='Simple1')
def my_pipeline_mini(year: int):
    dvop = dsl.VolumeOp(name="create_pvc",
                        resource_name="my-pvc-2",
                        size="5Gi",
                        modes=dsl.VOLUME_MODE_RWO)
    tldvop = dsl.VolumeOp(name="create_pvc",
                          resource_name="tld-volume-2",
                          size="100Mi",
                          modes=dsl.VOLUME_MODE_RWO)
    download_data_op = kfp.components.func_to_container_op(
        download_data, packages_to_install=['lxml', 'requests'])
    download_tld_info_op = kfp.components.func_to_container_op(
        download_tld_data,
        packages_to_install=['requests', 'pandas>=0.24', 'tables'])
    clean_data_op = kfp.components.func_to_container_op(
        clean_data, packages_to_install=['pandas>=0.24', 'tables'])

    step1 = download_data_op(year).add_pvolumes(
        {"/data_processing": dvop.volume})
    step2 = clean_data_op(input_path=step1.output).add_pvolumes(
        {"/data_processing": dvop.volume})
    step3 = download_tld_info_op().add_pvolumes({"/tld_info": tldvop.volume})


kfp.compiler.Compiler().compile(my_pipeline_mini, 'local-data-prep-2.zip')
#end::makePipeline[]

# In[ ]:

get_ipython().system('rm *.zip')

# In[ ]:


#tag::longPipeline[]
@kfp.dsl.pipeline(name='Simple1', description='Simple1')
def my_pipeline2(year: int):
    dvop = dsl.VolumeOp(name="create_pvc",
                        resource_name="my-pvc-2",
                        size="5Gi",
                        modes=dsl.VOLUME_MODE_RWO)
    tldvop = dsl.VolumeOp(name="create_pvc",
                          resource_name="tld-volume-2",
                          size="100Mi",
                          modes=dsl.VOLUME_MODE_RWO)

    download_data_op = kfp.components.func_to_container_op(
        download_data, packages_to_install=['lxml', 'requests'])
    download_tld_info_op = kfp.components.func_to_container_op(
        download_tld_data,
        packages_to_install=['requests', 'pandas>=0.24', 'tables'])
    clean_data_op = kfp.components.func_to_container_op(
        clean_data, packages_to_install=['pandas>=0.24', 'tables'])
#tag::add_feature_step[]
    prepare_features_op = kfp.components.func_to_container_op(
        prepare_features,
        packages_to_install=['pandas>=0.24', 'tables', 'scikit-learn'])
#end::add_feature_step[]

    step1 = download_data_op(year).add_pvolumes(
        {"/data_processing": dvop.volume})
    step2 = clean_data_op(input_path=step1.output).add_pvolumes(
        {"/data_processing": dvop.volume})
    step3 = download_tld_info_op().add_pvolumes({"/tld_info": tldvop.volume})
    step4 = prepare_features_op(input_path=step2.output,
                                tld_info_path=step3.output).add_pvolumes({
                                    "/data_processing":
                                    dvop.volume,
                                    "/tld_info":
                                    tldvop.volume
                                })


#end::longPipeline[]

kfp.compiler.Compiler().compile(my_pipeline2,
                                'local-data-and-feature-prep-2.zip')

# In[ ]:

client = kfp.Client()

# In[ ]:

my_experiment = client.create_experiment(name='local-data-prep-test-2')
my_run = client.run_pipeline(my_experiment.id,
                             'local-data-prep',
                             'local-data-and-feature-prep-2.zip',
                             params={'year': '2019'})

# If we were using Spamassasin or some other library installed in a different base container we would:

# In[ ]:

# Clean data with custom container
#tag::cleanDataWithContainer[]
clean_data_op = kfp.components.func_to_container_op(
    clean_data,
    base_image="{0}/kubeflow/spammassisan".format(container_registry),
    packages_to_install=['pandas>=0.24', 'tables'])
#end::cleanDataWithContainer[]

# In[ ]:


def train_func(input_path: String):
    from sklearn.cluster import KMeans
    from sklearn.model_selection import train_test_split

    train, test = train_test_split(data, test_size=0.1)

    kmeans = KMeans(n_clusters=2, random_state=42).fit(train)
    train_pred = kmeans.predict(train)
    test_pred = kmeans.predict(test)
    print(test_pred)
    # TODO: Dump the model somewhere you can use it later.


# And just like that, we've done it. We've created a Kubeflow Pipeline.
#
# So let's take a moment to step back and think, "what in the crazy-town-heck is going on here?!".  A valid question, and well spotted.  Each "Step" is going to be creating a container.  Maybe I should have noted that earlier when talking about attatching volumes, beacuse if you thougth I was doing that to a function, you'd probably think me quite insane.
#
# But, if you follow this code, and create this pipeline, download it and run it, you will see each "step" as a seperate container, downloading data, saving it to a `PVC` then passing some parameters to a next container, which also will load the `PVC`, etc. etc.
#
# ### Using Python to Create Containers, but not like a crazy person
#
# For completeness, let's last explore how to do all of these things using annotations.
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

# In[ ]:
