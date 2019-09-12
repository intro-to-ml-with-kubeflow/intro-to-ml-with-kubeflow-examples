import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem


@dsl.pipeline(
    name='Simple sci-kit KF Pipeline',
    description='A simple end to end sci-kit seldon kf pipeline'
)
def mnist_train_pipeline(
        output,
        project,
        docker_org="index.docker.io/seldonio",
        container_version="0.2"):

    vop = dsl.VolumeOp(
        name="create_pvc",
        resource_name="nfs-1",
        modes=dsl.VOLUME_MODE_RWO,
        size="10g")
    train = dsl.ContainerOp(
        name='sk-train',
        image=f"{docker_org}/skmnistclassifier_trainer:{container_version}",
        pvolumes={"/data": volume})

if __name__ == '__main__':
  import kfp.compiler as compiler
    
