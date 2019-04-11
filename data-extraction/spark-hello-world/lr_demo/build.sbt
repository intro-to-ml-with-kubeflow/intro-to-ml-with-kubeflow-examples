val sparkVersion = "2.3.1"

lazy val root = (project in file(".")).

  settings(
    inThisBuild(List(
      organization := "com.introtomlwithkubeflow.spark.demo",
      scalaVersion := "2.11.12"
    )),
    name := "basic.lr",
    version := "0.0.1",

    javacOptions ++= Seq("-source", "1.8", "-target", "1.8"),
    javaOptions ++= Seq("-Xms512M", "-Xmx2048M", "-XX:MaxPermSize=2048M", "-XX:+CMSClassUnloadingEnabled"),
    scalacOptions ++= Seq("-deprecation", "-unchecked"),
    parallelExecution in Test := false,
    fork := true,

    coverageHighlighting := true,

    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-streaming" % sparkVersion % "provided",
      "org.apache.spark" %% "spark-sql" % sparkVersion % "provided",
      "org.apache.spark" %% "spark-mllib" % sparkVersion % "provided",
      "ml.combust.mleap" %% "mleap-spark" % "0.13.0",

      "org.scalatest" %% "scalatest" % "3.0.1" % "test",
      "org.scalacheck" %% "scalacheck" % "1.13.4" % "test",
      "com.holdenkarau" %% "spark-testing-base" % "2.3.1_0.11.0" % "test"
    ),

    // uses compile classpath for the run task, including "provided" jar (cf http://stackoverflow.com/a/21803413/3827)
    run in Compile := Defaults.runTask(fullClasspath in Compile, mainClass in (Compile, run), runner in (Compile, run)).evaluated,

    scalacOptions ++= Seq("-deprecation", "-unchecked"),
    pomIncludeRepository := { x => false },

   resolvers ++= Seq(
      "sonatype-releases" at "https://oss.sonatype.org/content/repositories/releases/",
      "Typesafe repository" at "http://repo.typesafe.com/typesafe/releases/",
      "Second Typesafe repo" at "http://repo.typesafe.com/typesafe/maven-releases/",
      Resolver.sonatypeRepo("public")
    ),

    pomIncludeRepository := { x => false },
        mergeStrategy in assembly := {
      case m if m.toLowerCase.endsWith("manifest.mf") => MergeStrategy.discard
      case m if m.toLowerCase.endsWith("io.netty.versions.properties") => MergeStrategy.concat
      case m if m.toLowerCase.endsWith("services") => MergeStrategy.filterDistinctLines
      case m if m.toLowerCase.endsWith("git.properties") => MergeStrategy.discard
      case m if m.toLowerCase.endsWith("reference.conf") => MergeStrategy.filterDistinctLines
        // Travis is giving a weird error on netty I don't see locally :(
      case PathList("META-INF", "io.netty.versions.properties") => MergeStrategy.first
      case PathList("META-INF", "native", xs @ _*) => MergeStrategy.deduplicate
      case PathList("META-INF", "services", xs @ _ *) => MergeStrategy.filterDistinctLines
      case PathList("META-INF", xs @ _ *) => MergeStrategy.discard
      case PathList("javax", "servlet", xs @ _*) => MergeStrategy.last
      case PathList("org", "apache", xs @ _*) => MergeStrategy.last
      case PathList("org", "jboss", xs @ _*) => MergeStrategy.last
        // Start http://queirozf.com/entries/creating-scala-fat-jars-for-spark-on-sbt-with-sbt-assembly-plugin
      case PathList("org","aopalliance", xs @ _*) => MergeStrategy.last
      case PathList("javax", "inject", xs @ _*) => MergeStrategy.last
      case PathList("javax", "servlet", xs @ _*) => MergeStrategy.last
      case PathList("javax", "activation", xs @ _*) => MergeStrategy.last
      case PathList("org", "apache", xs @ _*) => MergeStrategy.last
      case PathList("com", "google", xs @ _*) => MergeStrategy.last
      case PathList("com", "esotericsoftware", xs @ _*) => MergeStrategy.last
      case PathList("com", "codahale", xs @ _*) => MergeStrategy.last
      case PathList("com", "yammer", xs @ _*) => MergeStrategy.last
        // End http://queirozf.com/entries/creating-scala-fat-jars-for-spark-on-sbt-with-sbt-assembly-plugin
      case PathList("com", "sun", "activation", "registries", xs @ _*) => MergeStrategy.last
      case PathList("com", "sun", "activation", "viewers", xs @ _*) => MergeStrategy.last
      case "about.html"  => MergeStrategy.rename
      case "reference.conf" => MergeStrategy.concat
      case m =>
        val oldStrategy = (assemblyMergeStrategy in assembly).value
        oldStrategy(m)
    },
    assemblyShadeRules in assembly := Seq(
      ShadeRule.rename("com.google.protobuf.**" -> "shadeproto.@1").inAll
    ),


    // publish settings
    publishTo := {
      val nexus = "https://oss.sonatype.org/"
      if (isSnapshot.value)
        Some("snapshots" at nexus + "content/repositories/snapshots")
      else
        Some("releases"  at nexus + "service/local/staging/deploy/maven2")
    }
  )
