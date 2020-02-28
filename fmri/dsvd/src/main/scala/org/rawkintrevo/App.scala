package org.rawkintrevo

import org.apache.mahout.math._
import org.apache.mahout.math.scalabindings._
import org.apache.mahout.math.drm._
import org.apache.mahout.math.scalabindings.RLikeOps._
import org.apache.mahout.math.drm.RLikeDrmOps._
import org.apache.mahout.sparkbindings._
import org.apache.mahout.math.decompositions._

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf

object App {
  def main(args: Array[String]) {


    val conf:SparkConf = new SparkConf()
      .setAppName("fMRI Example")
      .set("spark.kryo.referenceTracking", "false")
      .set("spark.kryo.registrator", "org.apache.mahout.sparkbindings.io.MahoutKryoRegistrator")
      .set("spark.kryoserializer.buffer", "32")
      .set("spark.kryoserializer.buffer.max" , "600m")
      .set("spark.serializer",	"org.apache.spark.serializer.KryoSerializer")

    //create spark context object
    val sc = new SparkContext(conf)
    implicit val sdc: org.apache.mahout.sparkbindings.SparkDistributedContext = sc2sdc(sc)


    val pathToMatrix = "/data/s.csv"  // todo make this an arg.

    val voxelRDD:DrmRdd[Int]  = sc.textFile(pathToMatrix).map(s => dvec( s.split(",")
        .map(f => f.toDouble)))
      .zipWithIndex
      .map(o => (o._2.toInt, o._1))

    val voxelDRM = drmWrap(voxelRDD)

    // k, p, q should all be cli parameters
    // k is rank of the output e.g. the number of eigenfaces we want out.
    // p is oversampling parameter,
    // and q is the number of additional power iterations
    // Read https://mahout.apache.org/users/dim-reduction/ssvd.html
    val k = 20
    val p = 15
    val q = 0
    val(drmU, drmV, s) = dssvd(voxelDRM, k, p, q)
    print("All is good")
    // todo save drmU / drmV for something (?)
  }
}
