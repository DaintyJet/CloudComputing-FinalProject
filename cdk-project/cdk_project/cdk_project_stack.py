from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as lb,
    aws_dynamodb as db,
    # aws_sqs as sqs,
)
import aws_cdk as cdk

from constructs import Construct

class CdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # We first need to create the lambda, this can be instantiated from a local zip file (likely what we will do) or from a s3 bucket.
        lambdaFunction = lb.Function(self, "WebInterface_Group6-8", 
                                    runtime=lb.Runtime.NODEJS_16_X, # This runtime can likely be changed!
                                    handler="index.handler", # Dont know what this is refering to, could be changed to index.js as it could refer to the entrypoint
                                    code=lb.Code.from_asset("C:\\Users\\matth\\OneDrive\\Documents\\GitHub\\CloudComputing-FinalProject\\packaging") # Temporary hard coded path, change to be dynamic later
                                    ) 
        # We will then need to create the dynamo DB database, this will then need to give the lambda read and write access.
        table = db.Table(self,"gamelist", # Name of table
                        partition_key=db.Attribute(name="uid", type=db.AttributeType.STRING) # Create partition key
                        
                        )
        
        # Configure Auto Scaling 
        read_scaling = table.auto_scale_read_capacity(min_capacity=5, max_capacity=20) # Values taken from CF. Sets min and max values 
        read_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale read 
        # needed to utilize cdk.Duration method/type to get the scaling parameters to work.

        write_scaling = table.auto_scale_write_capacity(min_capacity=5, max_capacity=20) # values taken from CF. Sets min and max values 
        write_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale write

        table.grant_full_access(lambdaFunction) # Restrict access later!
