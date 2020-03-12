#!/usr/bin/env bash

VERSION=0.6

docker build -t rawkintrevo/linreg_py:$VERSION .
docker push rawkintrevo/linreg_py:$VERSION