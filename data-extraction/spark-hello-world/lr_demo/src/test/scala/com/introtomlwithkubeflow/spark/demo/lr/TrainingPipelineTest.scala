package com.introtomlwithkubeflow.spark.demo.lr

/**
 * A simple test for the training pipeline
 */

import com.holdenkarau.spark.testing.{SharedSparkContext, Utils}

import org.apache.spark.sql._

import org.scalatest.FunSuite

import java.io.File

case class MyData(e1: Double, e2: Double, label: Double)

class TrainingPipelineTest extends FunSuite with SharedSparkContext {
  test("smok test"){
    val session = SparkSession.builder().getOrCreate()
    import session.implicits._

    val tempDir = Utils.createTempDir()

    val sampleDataRDD = sc.parallelize(Seq(
      MyData(1.0, 0.0, 1.0),
      MyData(2.0, 2.1, 2.0)))
    val sampleDataDS = session.createDataset(sampleDataRDD)
    val inputDataLocation = tempDir + "/input"
    val outputFile = tempDir + "/output.zip"
    sampleDataDS.write.format("csv").option("header", "true").save(inputDataLocation)

    val trainingPipeline = new TrainingPipeline(sc)
    trainingPipeline.train(inputDataLocation, outputFile)
    assert(new File(outputFile).exists())
  }
}
