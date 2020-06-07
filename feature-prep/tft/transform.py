#tag::imports[]
import tensorflow as tf
import tensorflow_transform as tft
from tensorflow_transform.tf_metadata import schema_utils
#end::imports[]

#tag::entry_point[]


def preprocessing_fn(inputs):
    #end::entry_point[]
    #tag::logic[]
    outputs = {}
    # TFT business logic goes here
    outputs["body_stuff"] = tft.compute_and_apply_vocabulary(inputs["body"],
                                                             top_k=1000)
    return outputs


#end::logic[]
