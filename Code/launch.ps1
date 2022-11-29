$ErrorActionPreference = "Stop"

$stackname="Team6stackName"
$templatefile="file://project.yaml"
$functionname="gameregister"
$rolename="lambda-ex"
$roleEnd= "arn:aws:iam::"+ $(aws sts get-caller-identity --query "Account").Trim('"') +":role/lambda-ex"

$VpcId="$(aws ec2 describe-vpcs --filter "Name=isDefault, Values=true" --query "Vpc[0].VpcId" --output text)"
$SubnetId="$(aws ec2 describe-subnets --filters "Name=vpc-id, Values=$VpcId" --query "Subnet[0].SubnetId" --output text)"

write-host "create stack ..."
aws cloudformation create-stack --template-body $templatefile --stack-name $stackname --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name $stackname

aws cloudformation describe-stacks --stack-name $stackname

write-host "create lambda execution role..."
aws iam create-role --role-name $rolename --assume-role-policy-document file://trustpolicy.json

write-host "add permission to lambda execution role..."
aws iam attach-role-policy --role-name $rolename --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name $rolename --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

write-host "create deployment package..."
Compress-Archive -LiteralPath ./index.js, ./index.html -DestinationPath ./function.zip

Start-Sleep -Seconds 5

write-host "create lambda function..."
#aws lambda create-function --function-name $functionname --zip-file fileb://function.zip --handler index.handler --runtime nodejs16.x --role arn:aws:iam::896231038669:role/lambda-ex
aws lambda create-function --function-name $functionname --zip-file fileb://function.zip --handler index.handler --runtime nodejs16.x --role $roleEnd
write-host "granting permissions to allow public access to function URL..."
aws lambda add-permission --function-name $functionname --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type "NONE" --statement-id url

write-host "generate function URL... "
aws lambda create-function-url-config --function-name $functionname --auth-type NONE 

write-host "prepare to launch function URL... "
$string = aws lambda get-function-url-config --function-name $functionname --output text

$URLString = ((Select-String '(http[s]?)(:\/\/)([^\s,]+)' -Input $string ).Matches.Value)

echo $URLString

START $URLString