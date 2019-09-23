# Sample Tensorflow Transform example on mnist data
import apache_beam as beam
import tensorflow as tf
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata
from tensorflow_transform.tf_metadata import dataset_schema


import requests
import tempfile
import os

# Hack to fetch the data. In the "real" world you would already have your data
mnist_path = "/tmp"
working_dir = "/tmp/out"

def fetch_data():
    train_url = "https://pjreddie.com/media/files/mnist_train.csv"
    test_url = "https://pjreddie.com/media/files/mnist_test.csv"
    response = requests.get(train_url)
    with open(mnist_path + "/train.csv", "wb") as f:
        content = response.content
        f.write(content)
    response = requests.get(test_url)
    with open(mnist_path + "/test.csv", "wb") as f:
        content = response.content
        f.write(content)
    



pixel_fields = ["pix-{}{}".format(i, j)
                for i in range(28)
                for j in range(28)]
label_field = "label"
def preprocessing_fn(inputs):
    # TODO: pre-process the fields to 0 to 1 range inputs
    result = {label_field: inputs[label_field]}
    for field_name in pixel_fields:
        result[field_name + "_norm"] = tft.scale_to_0_1(inputs[field_name])
    return result

input_data_schema = dataset_schema.from_feature_spec(dict(
    [(name, tf.io.FixedLenFeature([], tf.int64))
     for name in pixel_fields] +
    [(label_field, tf.io.FixedLenFeature([], tf.int64))]))

input_data_metadata = dataset_metadata.DatasetMetadata(input_data_schema)

fetch_data()
train_data_file = mnist_path + "/train.csv"

with beam.Pipeline() as pipeline:
    with tft_beam.Context(temp_dir=tempfile.mkdtemp()):
        columns = [label_field] + pixel_fields
        converter = tft.coders.CsvCoder(columns, input_data_schema)
        input_data = (
            pipeline
            | 'ReadInputData' >> beam.io.ReadFromText(train_data_file)
            | 'CleanInputData' >> beam.Map(converter.decode))
        input_dataset = (input_data, input_data_metadata)
        transformed_dataset, transform_fn = (
            input_dataset | tft_beam.AnalyzeAndTransformDataset(preprocessing_fn))
        transformed_data, transformed_metadata = transformed_dataset
        transformed_data_coder = tft.coders.ExampleProtoCoder(
          transformed_metadata.schema)

        # Write the resulting data out
        _ = (
          transformed_data
          | 'EncodeTrainData' >> beam.Map(transformed_data_coder.encode)
          | 'WriteTrainData' >> beam.io.WriteToTFRecord(
              os.path.join(working_dir, "data")))
        # We'll use the transform function later too
        _ = (
            transform_fn
            | 'WriteTransformFn' >> tft_beam.WriteTransformFn(working_dir))
