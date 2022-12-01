
# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

# Project Description.
Please refer to the main page's documentation for a description of hte project as a whole this referse specifically to the cdk implementation of the project.

## CDK 

```python
        table = db.Table(self,"gamelist", # Name of table
                        partition_key=db.Attribute(name="uid", type=db.AttributeType.STRING) # Create partition key
                        )
        table.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
```
This creates a dynamoDB table with the partition key uid of a string type, we apply the destroy remove policy so it is removed when **cdk destroy** is called  

```python
# Configure Auto Scaling 
        read_scaling = table.auto_scale_read_capacity(min_capacity=5, max_capacity=20) # Values taken from CF. Sets min and max values 
        read_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale read 
        
        
        write_scaling = table.auto_scale_write_capacity(min_capacity=5, max_capacity=20) # values taken from CF. Sets min and max values 
        write_scaling.scale_on_utilization(target_utilization_percent=50, scale_in_cooldown=cdk.Duration.seconds(600), scale_out_cooldown=cdk.Duration.seconds(50)) #Scale write
```
This configures the autoscaling for the dynamoDB instance, we will scale to a minial capacity of 5 reads/writes per second, and up to 20 per second ([generally](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ProvisionedThroughput.html))

we scale at 50% utlization 

This creates cloudwatch alarms so does that count :) (I did not know markdown made emojis)


```python
  lambdaFunction = lb.Function(self, "WebInterface_Group6-8", 
                                    runtime=lb.Runtime.NODEJS_16_X, # This runtime can likely be changed!
                                    handler="index.handler", # Dont know what this is refering to, could be changed to index.js as it could refer to the entrypoint
                                    code=lb.Code.from_asset(path.join("resources")), # Set to some directory relative to the current one
                                    environment=dict(
                                        BucketName=table.table_name
                                        #BUCKET=lambdaBucket.bucket_name
                                    ),
                                    insights_version=lb.LambdaInsightsVersion.VERSION_1_0_98_0
                                    ) 
```
This creates the lambda function it is a NodeJS runtime that will run a index.js file loaded from resources. We provide an environment variable of the bucket name as the name is not guaranteed to be what we specify it, and the JS file needs to refer to it in order to access the DB. Insights provides various cloudwatch metrics that may be useful!

