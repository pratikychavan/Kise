#!/bin/bash
access_key=
secret_key=
region=
aws configure set aws_access_key_id $access_key \
&& aws configure set aws_secret_access_key $secret_key \
&& aws configure set default.region $region \
&& aws configure set default.output json