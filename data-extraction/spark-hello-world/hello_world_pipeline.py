import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem

from string import Template
import json

@dsl.pipeline(
    name='Simple spark pipeline demo',
    description='Shows how to use Spark operator inside KF'
)
def spark_hello_world_pipeline(
        jar_location="gcs://....",
        tf_job_image="..."):
    spark_json_template = Template("""
{
    "apiVersion": "sparkoperator.k8s.io/v1beta2",
    "kind": "SparkApplication",
    "metadata": {
      "name": "spark-frank",
      "namespace": "kubeflow"},
    "spec": {
      "type": "Scala",
      "mode": "cluster",
      "mainApplicationFile": "$jar_location"
    }""")
    spark_json = spark_json_template.substitute({
        'jar_location': jar_location})
    spark_job = json.loads(spark_json)
    spark_resource = dsl.ResourceOp(
        name='spark-job',
        k8s_resource=spark_job,
        success_condition='status.state == Succeeded')
    train = dsl.ContainerOp(
        name='train',
        image=tf_job_image,
    ).after(spark_resoure)
