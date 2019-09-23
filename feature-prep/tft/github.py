# Sample Tensorflow Transform example on github data
import tensorflow as tf
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata
from tensorflow_transform.tf_metadata import dataset_schema

text_fields = (["lineText"] +
               map(lambda x: f"nextLine{x}", range(0, 4)) +
               map(lambda x: f"previousLine{x}", range(0, 4)))

def preprocessing_fn(inputs):
    text_fields = []
    # Keep the original data and add more to it.
    result = inputs.copy()
    # Figure out the vocabulary for our text fields.
    for field_name in text_fields:
        field = inputs[field_name]
        tokens = tf.strings.split(text, " ")
        bag_of_words = tft.bag_of_words(tokens, range(1,3), seperator=" ")
        indices = tft.compute_and_apply_vocabulary(bag_of_words)
        bow_indices, weights = tft.tfidf(line_indices)
        outputs[f"{field_name}_bow_indices"] = bow_indices
        outputs[f"{field_name}_weight"] weights
    return result

input_data_schema = dataset_schema.from_feature_spec(dict(
    [(name, tf.io.FixedLenFeature([], tf.string))
     for name in text_fields] +
    ['commented': tf.FixedLenFeature([], tf.boolean),
    'add': tf.FixedLenFeature([], tf.boolean),
     'line_length': tf.FixedLenFeature([], tf.int32])))

input_data_metadata = dataset_metadata.DatasetMetadata(input_data_schema)

with beam.Pipeline() as pipeline:
    with tft_beam.Context(temp_dir=tempfile.mkdtemp()):
        columns = text_fields + ["commented", "add", "line_length"]
        converter = tft.coders.CsvCoder(columns, input_data_schema)
        input_data = (
            pipeline
            | 'ReadInputData' >> beam.io.ReadFromText(train_data_file)
            | 'CleanInputData' >> MapAndFilterErrors(converter.decode))
        input_dataset = (input_data, input_data_metadata)
        transformed_dataset, transform_fn = (
            input_dataset | tft_beam.AnalyzeAndTransformDataset(preprocessing_fn))
        transformed_data, transfored_metadata = transformed_dataset
        transformed_data_coder = tft.coders.ExampleProtoCoder(
          transformed_metadata.schema)

        # Write the resulting data out
        _ = (
          transformed_data
          | 'EncodeTrainData' >> beam.Map(transformed_data_coder.encode)
          | 'WriteTrainData' >> beam.io.WriteToTFRecord(
              os.path.join(working_dir, TRANSFORMED_TRAIN_DATA_FILEBASE)))
        # We'll use the transform function later too
        _ = (
            transform_fn
            | 'WriteTransformFn' >> tft_beam.WriteTransformFn(working_dir))
