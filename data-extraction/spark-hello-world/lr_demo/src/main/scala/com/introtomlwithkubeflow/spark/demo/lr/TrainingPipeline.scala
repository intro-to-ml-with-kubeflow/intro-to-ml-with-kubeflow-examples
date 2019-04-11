package com.introtomlwithkubeflow.spark.demo.lr

import java.nio.file.{Files, Paths}


import ml.combust.bundle.BundleFile
import ml.combust.mleap.spark.SparkSupport._
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.spark.ml.bundle.SparkBundleContext // Actually an mleap import
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.catalyst.ScalaReflection
import org.apache.spark.ml.Transformer
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.feature._
import org.apache.spark.ml.regression._
import resource._


class TrainingPipeline(sc: SparkContext) {
  val session = SparkSession.builder().getOrCreate()
  import session.implicits._

  def train(input: String, outputFile: String) = {
    val trainingData = session.read.format("csv")
      .option("inferSchema", "true").option("header", "true").load(input)
    val vectorizer = new VectorAssembler().setInputCols(Array("e1", "e2")).setOutputCol("features")
    val lr = new GeneralizedLinearRegression()
      .setFamily("gaussian")
      .setLink("identity")
      .setMaxIter(10)
      .setRegParam(0.3)
    val pipeline = new Pipeline().setStages(Array(
      vectorizer,
      lr))
    val fit = pipeline.fit(trainingData)
    // Serialize the fit pipeline
    val resultData = fit.transform(trainingData)
    val localFile = "/tmp/mleap.zip"
    val localOutput = s"jar:file:${localFile}"
    val sbc = SparkBundleContext().withDataset(resultData)
    for(bf <- managed(BundleFile(localOutput))) {
      fit.writeBundle.save(bf)(sbc).get
    }
    // We only have one file so its k
    val modelBinary = Files.readAllBytes(Paths.get(localFile))
    val fs = FileSystem.get(sc.hadoopConfiguration)
    val out = fs.create(new Path(outputFile))
    out.write(modelBinary);
    out.close();
  }
}
