#!/bin/bash
#tag::ubuntu[]
apt-get install google-cloud-sdk
#end::ubuntu[]
apt-get remove google-cloud-sdk
#tag::general[]
curl https://sdk.cloud.google.com | bash
#end::general[]
