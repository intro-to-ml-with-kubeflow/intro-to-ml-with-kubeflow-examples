import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem

from string import Template
import json

@dsl.pipeline(
    name='Simple sci-kit KF Pipeline',
    description='A simple end to end sci-kit seldon kf pipeline'
)
def mnist_train_pipeline(
        docker_org="index.docker.io/seldonio",
        train_container_version="0.2",
        serve_container_version="0.1"):

    vop = dsl.VolumeOp(
        name="create_pvc",
        resource_name="nfs-1",
        modes=dsl.VOLUME_MODE_RWO,
        size="10G")
    volume = vop.volume
    train = dsl.ContainerOp(
        name='sk-train',
        image=f"{docker_org}/skmnistclassifier_trainer:{train_container_version}",
        pvolumes={"/data": volume})

    seldon_serving_json_template = Template("""
{
	"apiVersion": "machinelearning.seldon.io/v1alpha2",
	"kind": "SeldonDeployment",
	"metadata": {
		"labels": {
			"app": "seldon"
		},
		"name": "mnist-classifier"
	},
	"spec": {
		"annotations": {
			"deployment_version": "v1",
			"project_name": "MNIST Example"
		},
		"name": "mnist-classifier",
		"predictors": [
			{
				"annotations": {
					"predictor_version": "v1"
				},
				"componentSpecs": [
					{
						"spec": {
							"containers": [
								{
									"image": "$dockerreposerving:$dockertagserving",
									"imagePullPolicy": "Always",
									"name": "mnist-classifier",
									"volumeMounts": [
										{
											"mountPath": "/data",
											"name": "persistent-storage"
										}
									]
								}
							],
							"terminationGracePeriodSeconds": 1,
							"volumes": [
								{
									"name": "persistent-storage",
									"persistentVolumeClaim": {
											"claimName": "$modelpvc"
									}
								}
							]
						}
					}
				],
				"graph": {
					"children": [],
					"endpoint": {
						"type": "REST"
					},
					"name": "mnist-classifier",
					"type": "MODEL"
				},
				"name": "mnist-classifier",
				"replicas": 1
			}
		]
	}
}    
""")
    seldon_serving_json = seldon_serving_json_template.substitute({
        'dockerreposerving': f"{docker_org}/skmnistclassifier_runtime",
        'dockertagserving': str(serve_container_version),
        'modelpvc': vop.outputs["name"]})

    seldon_deployment = json.loads(seldon_serving_json)

    serve = dsl.ResourceOp(
        name='serve',
        k8s_resource=seldon_deployment,
        success_condition='status.state == Available'
    ).after(train)

# If we're called directly create an expirement and run
if __name__ == '__main__':
    pipeline_func = mnist_train_pipeline
    pipeline_filename = pipeline_func.__name__ + '.pipeline.zip'
    import kfp.compiler as compiler
    compiler.Compiler().compile(pipeline_func, pipeline_filename)
    expirement_name = "cheese"
    experiment = client.create_experiment(expirement_name)
    run_name = pipeline_func.__name__ + ' run'
    run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)
    print(run_result)
