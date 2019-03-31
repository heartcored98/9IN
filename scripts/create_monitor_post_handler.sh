# Additional dependency package Ref : https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-venv
# Configure CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
# Handling Lambda with Command line : https://hackernoon.com/exploring-the-aws-lambda-deployment-limits-9a8384b0bec3
# AWS Lambda CLI Documentation : https://docs.aws.amazon.com/cli/latest/reference/lambda/update-function-configuration.html
# AWS CloudWatch Rule : https://docs.amazonaws.cn/en_us/AmazonCloudWatch/latest/events/RunLambdaSchedule.html
read -e -p "Monitor Post Function Name: " -i "guin_monitor_post" function_name
read -e -p "Post Content Function Name: " -i "guin_post_content" content_function_name
read -e -p "TEST MODE? (y/n): " -i "y" TEST_MODE

if [[ $TEST_MODE == n ]]
then
    function_name="${function_name}_deploy"
    content_function_name="${content_function_name}_deploy"

else
    function_name="${function_name}_test"
    content_function_name="${content_function_name}_test"
fi

env_variables="STOP_WORDS=카풀/판매/팝니다/구매/구입/삽니다"

cd ../
cp packages.zip ori_packages.zip

# Attatch source code into packages.zip inside src directory
mv packages.zip src/packages.zip
cd src
zip -g packages.zip parser_post.py pusher_telegram.py handler_monitor_post.py s3_utils.py utils.py
cd ..
mv src/packages.zip packages.zip
zip -g packages.zip settings.yml

# Prepare packages for deploying
mv packages.zip deploys.zip
mv ori_packages.zip packages.zip
aws s3 cp deploys.zip s3://guin-bucket/
rm deploys.zip

aws lambda delete-function --function-name $function_name

if [[ $TEST_MODE == n ]]
then
    echo $env_variables
    aws lambda create-function --function-name $function_name \
    --runtime python3.6 \
    --role arn:aws:iam::915999582461:role/role_guin \
    --handler handler_monitor_post.ara_wanted_handler \
    --region ap-northeast-2 \
    --zip-file fileb://dummy.zip \
    --environment Variables={"TEST_MODE=false,ARTICLE_PARSER_LAMBDA=${content_function_name},${env_variables}"}
else
    aws lambda create-function --function-name $function_name \
    --runtime python3.6 \
    --role arn:aws:iam::915999582461:role/role_guin \
    --handler handler_monitor_post.ara_wanted_handler \
    --region ap-northeast-2 \
    --zip-file fileb://dummy.zip \
    --environment Variables={"TEST_MODE=true,ARTICLE_PARSER_LAMBDA=${content_function_name},${env_variables}"}
fi

aws lambda update-function-code --function-name $function_name --region ap-northeast-2 --s3-bucket guin-bucket --s3-key deploys.zip
aws lambda update-function-configuration --function-name $function_name \
--region ap-northeast-2 \
--timeout 10 \
--memory-size 128

# Add 1 minute-period trigger
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
    aws events put-rule --name 1min_trigger_test --schedule-expression 'rate(1 minute)'
    aws lambda add-permission \
    --function-name $function_name \
    --statement-id 1min-event-test \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:ap-northeast-2:915999582461:rule/1min_trigger_test
fi