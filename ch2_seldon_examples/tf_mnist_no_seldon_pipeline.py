# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Kubeflow Pipelines MNIST example

Run this script to compile pipeline
"""

import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem

gcs_or_pvc = 'PVC'


@dsl.pipeline(name='MNIST',
              description='A pipeline to train and serve the MNIST example.')
def mnist_pipeline(gcs_bucket=None,
                   train_steps='200',
                   learning_rate='0.01',
                   batch_size='100'):
    """
    Pipeline with three stages:
      1. train an MNIST classifier
      2. deploy a tf-serving instance to the cluster
      3. deploy a web-ui to interact with it
    """

    vop = None
    volume = None
    if gcs_or_pvc == "PVC":
        vop = dsl.VolumeOp(name="create_pvc",
                           resource_name="nfs-1",
                           modes=dsl.VOLUME_MODE_RWO,
                           size="10G")
        volume = vop.volume

    train = dsl.ContainerOp(
        name='train',
        image=
        'gcr.io/kubeflow-examples/mnist/model:v20190304-v0.2-176-g15d997b',
        arguments=[
            "/opt/model.py", "--tf-export-dir", gcs_bucket or "/mnt",
            "--tf-train-steps", train_steps, "--tf-batch-size", batch_size,
            "--tf-learning-rate", learning_rate
        ])

    serve_args = [
        '--model-export-path', gcs_bucket or "/mnt", '--server-name',
        "mnist-service"
    ]
    if gcs_or_pvc != 'GCS':
        serve_args.extend(
            ['--cluster-name', "mnist-pipeline", '--pvc-name', volume])

    serve = dsl.ContainerOp(
        name='serve',
        image='gcr.io/ml-pipeline/ml-pipeline-kubeflow-deployer:'
        '7775692adf28d6f79098e76e839986c9ee55dd61',
        arguments=serve_args)
    serve.after(train)

    webui_args = [
        '--image', 'gcr.io/kubeflow-examples/mnist/web-ui:'
        'v20190304-v0.2-176-g15d997b-pipelines', '--name', 'web-ui',
        '--container-port', '5000', '--service-port', '80', '--service-type',
        "LoadBalancer"
    ]

    web_ui = dsl.ContainerOp(
        name='web-ui',
        image='gcr.io/kubeflow-examples/mnist/deploy-service:latest',
        arguments=webui_args)
    web_ui.after(serve)

    steps = [train, serve, web_ui]
    for step in steps:
        if gcs_or_pvc == 'GCS':
            step.apply(gcp.use_gcp_secret('user-gcp-sa'))
        else:
            step.after(vop)
            step.add_pvolumes({"/mnt": volume})


if __name__ == '__main__':
    import kfp.compiler as compiler
    compiler.Compiler().compile(mnist_pipeline, __file__ + '.tar.gz')
