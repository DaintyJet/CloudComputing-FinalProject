$ErrorActionPreference = "Stop"

$stackname="Team6stackName"
$templatefile="file://project.yaml"
$rolename="lambda-ex"
$functionname="gameregister"

$VpcId="$(aws ec2 describe-vpcs --filter "Name=isDefault, Values=true" --query "Vpc[0].VpcId" --output text)"
$SubnetId="$(aws ec2 describe-subnets --filters "Name=vpc-id, Values=$VpcId" --query "Subnet[0].SubnetId" --output text)"

write-host "delete stack ..."
aws cloudformation delete-stack --stack-name $stackname 

write-host "detaching policies..."
aws iam detach-role-policy --role-name $rolename --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-role-policy --role-name $rolename --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

write-host "delete lambda execution role..."
aws iam delete-role --role-name $rolename


write-host "delete deployment package..."
rm ./function.zip

write-host "delete lambda..."
aws lambda delete-function --function-name $functionname