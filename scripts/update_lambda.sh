#!/usr/bin/env bash

aws lambda create-function --region ap-northeast-2 --function-name test_guin --zip-file fileb://function.zip --runtime python3.6 --handler ara_wanted_handler --role arn:aws:iam::915999582461:role/role_guin
