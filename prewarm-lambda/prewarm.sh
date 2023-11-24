#Cloudfront url: d1zi40b7x5dwgb.cloudfront.net
#Lambda function name: cloudfront_prewarm
#Need aws cli

read -p "please input funcion exec role arn:" exec_role_arn
read -p "Please input your cloudfront link: " cfn_link

#!/bin/bash

function_exists=$(aws lambda list-functions --query "Functions[?FunctionName=='cloudfront_prewarm'].FunctionName" --output text)

if [ "$function_exists" == "cloudfront_prewarm" ]; then
  echo "Lambda function 'cloudfront_prewarm' already exists. Skipping creation."
  for file in `cat file.txt`
  do
	  echo $file
	  payload="{\"filename\":\"$file\",\"cloudfront_url\":\"$cfn_link\"}"
	  aws lambda invoke --function-name cloudfront_prewarm --invocation-type Event --cli-binary-format raw-in-base64-out --payload $payload o.out
  done
else
  echo "Creating Lambda function 'cloudfront_prewarm'..."

aws lambda create-function \
  --function-name cloudfront_prewarm \
  --runtime python3.11 \
  --role $exec_role_arn \
  --handler cloudfront_prewarm.lambda_handler \
  --zip-file fileb://cloudfront_prewarm.zip \
  --memory-size 1024 \
  --timeout 900

echo "waiting function active........."
sleep 5
for file in `cat file.txt`
do
echo $file
payload="{\"filename\":\"$file\",\"cloudfront_url\":\"$cfn_link\"}"
aws lambda invoke --function-name cloudfront_prewarm --invocation-type Event --cli-binary-format raw-in-base64-out --payload $payload o.out 
done
fi
