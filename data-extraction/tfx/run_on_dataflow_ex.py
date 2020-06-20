#tag::example[]
generated_output_uri = root_output_uri + kfp.dsl.EXECUTION_ID_PLACEHOLDER
beam_pipeline_args = [
    '--runner=DataflowRunner',
    '--project=' + project_id,
    '--temp_location=' + root_output_uri + '/tmp'),
    '--region=' + gcp_region,
    '--disk_size_gb=50', # Adjust as needed
]

records_example = tfx_csv_gen(
    input_uri=fetch.output, # Must be on distributed storage
    beam_pipeline_args=beam_pipeline_args,
    output_examples_uri=generated_output_uri)
#end::example[]
