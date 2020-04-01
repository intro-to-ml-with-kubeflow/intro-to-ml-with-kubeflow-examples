#!/bin/bash

img='lightbend/mlflow'
tag='0.1'
docker build -t $img:$tag .

