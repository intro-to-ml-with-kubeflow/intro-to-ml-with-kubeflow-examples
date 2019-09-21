# Sample Tensorflow Transform example on mnist data
import tensorflow as tf
import tensorflow_transform as tft
import tensorflow_transform.beam as tft_beam

pixel_fields = ...
def preprocessing_fn(inputs):
