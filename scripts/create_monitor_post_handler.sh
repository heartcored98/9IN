# Additional dependency package Ref : https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-venv
# Configure CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
# Handling Lambda with Command line : https://hackernoon.com/exploring-the-aws-lambda-deployment-limits-9a8384b0bec3
# AWS Lambda CLI Documentation : https://docs.aws.amazon.com/cli/latest/reference/lambda/update-function-configuration.html
# AWS CloudWatch Rule : https://docs.amazonaws.cn/en_us/AmazonCloudWatch/latest/events/RunLambdaSchedule.html
read -e -p "Function Name: " -i "test_guin" function_name
read -e -p "TEST MODE? (y/n): " -i "y" TEST_MODE


cd ../
cp packages.zip ori_packages.zip
zip -g packages.zip src/parser_post.py src/pusher_telegram.py src/handler_monitor_post.py src/s3_utils.py src/utils.py settings.yml
mv packages.zip deploys.zip
mv ori_packages.zip packages.zip
aws s3 cp deploys.zip s3://guin-bucket/
rm deploys.zip

aws lambda delete-function --function-name $function_name
aws lambda create-function --function-name $function_name --runtime python3.6 --role arn:aws:iam::915999582461:role/role_guin --handler handler_monitor_post.ara_wanted_handler --region ap-northeast-2 --zip-file fileb://dummy.zip
aws lambda update-function-code --function-name $function_name --region ap-northeast-2 --s3-bucket guin-bucket --s3-key deploys.zip
aws lambda update-function-configuration --function-name $function_name \
--region ap-northeast-2 \
--timeout 10 \
--memory-size 128

if [[ $TEST_MODE == n ]]
then
    aws events put-rule --name 1min_trigger_deploy --schedule-expression 'rate(1 minute)'
    aws lambda add-permission \
    --function-name $function_name \
    --statement-id 1min-event-deploy \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:ap-northeast-2:915999582461:rule/1min_trigger_deploy
else
    aws events put-rule --name 1min_trigger --schedule-expression 'rate(1 minute)'
    aws lambda add-permission \
    --function-name $function_name \
    --statement-id 1min-event \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:ap-northeast-2:915999582461:rule/1min_trigger
fi