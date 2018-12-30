# Additional dependency package Ref : https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-venv
# Configure CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
# Handling Lambda with Command line : https://hackernoon.com/exploring-the-aws-lambda-deployment-limits-9a8384b0bec3
# AWS Lambda CLI Documentation : https://docs.aws.amazon.com/cli/latest/reference/lambda/update-function-configuration.html
# AWS CloudWatch Rule : https://docs.amazonaws.cn/en_us/AmazonCloudWatch/latest/events/RunLambdaSchedule.html

cd ../
cp packages.zip ori_packages.zip
zip -g packages.zip post_parser.py pusher.py run_monitoring.py s3_utils.py settings.yml
mv packages.zip deploys.zip
mv ori_packages.zip packages.zip
#aws s3 cp deploys.zip s3://guin-bucket/

read -p 'Function Name: ' function_name
aws lambda delete-function --function-name $function_name
aws lambda create-function --function-name $function_name --runtime python3.6 --role arn:aws:iam::915999582461:role/role_guin --handler run_monitoring.ara_wanted_handler --region ap-northeast-2 --zip-file fileb://sample.zip
aws lambda update-function-code --function-name $function_name --region ap-northeast-2 --s3-bucket guin-bucket --s3-key deploys.zip
aws lambda update-function-configuration --function-name $function_name --region ap-northeast-2 --timeout 10 --memory-size 128

#aws events put-rule --name 1min_trig schedule-expression 'rate(1 minute)'
aws lambda add-permission \
--function-name $function_name \
--statement-id 1min-event \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:ap-northeast-2:915999582461:rule/1min_trigger


