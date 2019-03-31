# Additional dependency package Ref : https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-venv
# Configure CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
# Handling Lambda with Command line : https://hackernoon.com/exploring-the-aws-lambda-deployment-limits-9a8384b0bec3
# AWS Lambda CLI Documentation : https://docs.aws.amazon.com/cli/latest/reference/lambda/update-function-configuration.html
# AWS CloudWatch Rule : https://docs.amazonaws.cn/en_us/AmazonCloudWatch/latest/events/RunLambdaSchedule.html
# Handling Large Dependency File : https://hackernoon.com/exploring-the-aws-lambda-deployment-limits-9a8384b0bec3
# Add 1 minute trigger schedule rule : https://docs.amazonaws.cn/en_us/AmazonCloudWatch/latest/events/RunLambdaSchedule.html
# AWS Lambda Selenium : http://robertorocha.info/setting-up-a-selenium-web-scraper-on-aws-lambda-with-python/
# AWS CLI environment variable : https://docs.aws.amazon.com/cli/latest/reference/lambda/update-function-configuration.html
#                                https://docs.aws.amazon.com/lambda/latest/dg/env_variables.html

# Docker Installation link : https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/
# Docker deb link : https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_18.09.0~3-0~ubuntu-xenial_amd64.deb
# Docker-compose install link : https://stackoverflow.com/questions/36685980/docker-is-installed-but-docker-compose-is-not-why

read -e -p 'Function Name: ' -i "guin_post_content" function_name
read -e -p 'Max Length of Message?: ' -i "120" MAX_LEN
read -e -p "TEST MODE? (y/n): " -i "y" TEST_MODE

if [[ $TEST_MODE == n ]]
then
    function_name="${function_name}_deploy"
else
    function_name="${function_name}_test"
fi

cd ../


#cd packages

# Get chromedriver
#curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
#unzip chromedriver.zip

# Get Headless-chrome
#curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
#unzip headless-chromium.zip

# Clean
#rm headless-chromium.zip chromedriver.zip
#cd ..

cp packages_sele.zip ori_packages_sele.zip

# Attach source code into packages_sele.zip inside src directory
mv packages_sele.zip src/packages_sele.zip
cd src
zip -g packages_sele.zip handler_post_content.py parser_content.py pusher_telegram.py s3_utils.py utils.py selenium_driver.py
cd ..
mv src/packages_sele.zip packages_sele.zip

# Attach chromedriver and selenium into packages_sele.zip inside packages directory
mv packages_sele.zip packages/packages_sele.zip
cd packages
zip -g packages_sele.zip chromedriver headless-chromium
cd ..
mv packages/packages_sele.zip packages_sele.zip

# Attach deploy settings
zip -g packages_sele.zip settings.yml
mv packages_sele.zip deploys_selenium.zip
mv ori_packages_sele.zip packages_sele.zip
aws s3 cp deploys_selenium.zip s3://guin-bucket/
rm deploys_selenium.zip

aws lambda delete-function --function-name $function_name
aws lambda create-function --function-name $function_name \
--runtime python3.6 \
--role arn:aws:iam::915999582461:role/role_guin \
--handler handler_post_content.article_handler \
--region ap-northeast-2 \
--zip-file fileb://dummy.zip \
--environment Variables={"PATH=/var/task/bin:/var/task/,PYTHONPATH=/var/task/src:/var/task/lib,${MAX_LEN}=120}"



aws lambda update-function-code --function-name $function_name --region ap-northeast-2 --s3-bucket guin-bucket --s3-key deploys_selenium.zip
aws lambda update-function-configuration --function-name $function_name \
--region ap-northeast-2 \
--timeout 30 \
--memory-size 350


