package com.introtomlwithkubeflow.spark.demo.lr

import org.apache.spark.{SparkConf, SparkContext}


/**
  * Use this when submitting the app to a cluster with spark-submit
  * */
object TrainingApp extends App{
  val (inputFile, outputFile) = (args(0), args(1))

  // spark-submit command should supply all necessary config elements
  Runner.run(new SparkConf(), inputFile, outputFile)
}

object Runner {
  def run(conf: SparkConf, inputFile: String, outputFile: String): Unit = {
    val sc = new SparkContext(conf)
    val trainer = new TrainingPipeline(sc)
    trainer.train(inputFile, outputFile)
  }
}
