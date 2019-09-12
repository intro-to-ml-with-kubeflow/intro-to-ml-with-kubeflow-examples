import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem


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
    serving = dsl.ContainerOp(
        name="mnist-classifier-serving",
        image=f"{docker_org}/skmnistclassifier_runtime:{serve_container_version}",
        pvolumes={"/data": train.pvolume}).after(train)

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
