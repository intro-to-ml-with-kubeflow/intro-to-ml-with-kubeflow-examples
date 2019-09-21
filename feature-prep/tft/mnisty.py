# Sample Tensorflow Transform example on mnist data
import tensorflow as tf
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam

pixel_fields = ...
label_field = ...
def preprocessing_fn(inputs):
    # TODO: pre-process the fields to 0 to 1 range inputs
