from os import path
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as lb,
    aws_dynamodb as db,
    # aws_sqs as sqs,
)


class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # We first need to create the bucket to store the lambda
        #lambdaBucket = s3.Bucket(self, "group6-8Bucket")

       
        # We will then need to create the dynamo DB database, this will then need to give the lambda read and write access.
        table = db.Table(self,"gamelist", # Name of table
                        partition_key=db.Attribute(name="uid", type=db.AttributeType.STRING) # Create partition key
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
                                        #BUCKET=lambdaBucket.bucket_name
                                    )
                                    #insights_version=lb.LambdaInsightsVersion.VERSION_1_0_98_0
                                    ) 
                                    
        # Grand read write access of the S3 to the lambda
        #lambdaBucket.grant_read_write(lambdaFunction)

        # Create the lambda's URL, allow anyone to connect to it
        lambdaFunctionURL = lambdaFunction.add_function_url(auth_type=lb.FunctionUrlAuthType.NONE)
        
        # Output the URL to the output dir
        cdk.CfnOutput(self, "Game Repository URL",
                    value=lambdaFunctionURL.url
        )

        cdk.CfnOutput(self, "Tablename", value=table.table_name)

        table.grant_read_write_data(lambdaFunction) # Restrict access later!

        # Would we like to implement alarms? https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dynamodb/README.html#alarm-metrics
