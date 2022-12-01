from os import path
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as lb,
    aws_dynamodb as db,
    aws_cloudwatch as cloudwatch
    # aws_sqs as sqs,
)


class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
       
        # We will then need to create the dynamo DB database, this will then need to give the lambda read and write access.
        table = db.Table(self,"gamelist", # Name of table
                        partition_key=db.Attribute(name="entryId", type=db.AttributeType.STRING) # Create partition key
                        )
        table.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        
        # Configure Auto Scaling 
        read_scaling = table.auto_scale_read_capacity(min_capacity=5, max_capacity=20) # Values taken from CF. Sets min and max values 
        read_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale read 
        # needed to utilize cdk.Duration method/type to get the scaling parameters to work.

        write_scaling = table.auto_scale_write_capacity(min_capacity=5, max_capacity=20) # values taken from CF. Sets min and max values 
        write_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale write
        
        
        # We then need to create the lambda, this can be instantiated from a local zip file (likely what we will do) or from a s3 bucket.
        lambdaFunction = lb.Function(self, "WebInterface_Group6-8", 
                                    runtime=lb.Runtime.NODEJS_16_X, # This runtime can likely be changed!
                                    handler="index.handler", # Dont know what this is refering to, could be changed to index.js as it could refer to the entrypoint
                                    code=lb.Code.from_asset(path.join("resources")), # Set to some directory relative to the current one
                                    environment=dict(
                                        BucketName=table.table_name
                                    ),
                                    insights_version=lb.LambdaInsightsVersion.VERSION_1_0_98_0
                                    ) 
                                    

        # Create the lambda's URL, allow anyone to connect to it
        lambdaFunctionURL = lambdaFunction.add_function_url(auth_type=lb.FunctionUrlAuthType.NONE)
        
        # Output the URL to the output dir
        cdk.CfnOutput(self, "Game Repository URL",
                    value=lambdaFunctionURL.url
        )

        table.grant_read_write_data(lambdaFunction) 

        # Would we like to implement alarms? https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dynamodb/README.html#alarm-metrics
        # Basic Alarms for lambda 
        lambdaFunctionInvokation = lambdaFunction.metric_invocations(
            period=cdk.Duration.seconds(30)
        )

        lambdaFunctionErrors = lambdaFunction.metric_errors(
            period=cdk.Duration.seconds(10)
        )

        invocationAlarm = cloudwatch.Alarm(self, "Lambda Invocation Count Alarm", 
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=5,
            evaluation_periods=1,
            alarm_description="This is a simple alarm to notify us of when there are 5 (or more) concurrently executing lambda functions",
            metric=lambdaFunctionInvokation
        )
        invocationAlarm.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        errorAlarm = cloudwatch.Alarm(self, "Lambda Invocation Error Alarm", 
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
            alarm_description="This is a simple alarm to notify us of when there are 1 (or more) concurrently executing lambda functions with errors",
            metric=lambdaFunctionErrors
        )
        errorAlarm.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Basic alarms for Dynamo DB
        DynamoRead= table.metric_consumed_read_capacity_units(
            period=cdk.Duration.minutes(1)
        )
        # DynamoWrite

        PutMetric = table.metric_throttled_requests_for_operations(
            operations=[db.Operation.PUT_ITEM],
            period=cdk.Duration.minutes(1)
        )

        FailedDynamo = table.metric_conditional_check_failed_requests(
            period=cdk.Duration.seconds(30)
        )

        putThrottleAlarm = cloudwatch.Alarm(self, "Dynamo Put Alarm",
            metric=PutMetric,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=2
        )
        putThrottleAlarm.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        failedDynamoAlarm = cloudwatch.Alarm(self, "Dynamo Failed Operation Alarm",
            metric=FailedDynamo,
            threshold=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=1
        )
        failedDynamoAlarm.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        readDynamoAlarm = cloudwatch.Alarm(self, "Dynamo Read Alarm",
            metric=DynamoRead,
            threshold=50,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            evaluation_periods=10
        )
        readDynamoAlarm.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

