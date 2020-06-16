#!/usr/bin/env bash
set -e

# 1st arg- case number (leading zero required if < 10), defaults to case1

if [ -z "${1}" ]
then
      CASE="01"
else
      CASE="${1}"
fi



echo "Downloading DICOMs"
# If not on GCP need to download this
gsutil cp gs://covid-dicoms/covid-dicoms.tar.gz /tmp/covid-dicoms.tar.gz
tar -xzf /tmp/covid-dicoms.tar.gz -C /tmp

mv "/tmp/case0${CASE}/axial" /data/dicom



