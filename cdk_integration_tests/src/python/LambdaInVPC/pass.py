from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_sam as sam

class MyLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        my_vpc = ec2.Vpc(
            self,
            "MyVPC",
            max_azs=2,  # Set the number of Availability Zones as needed
        )

        # Create a Lambda function in the VPC
        my_lambda_function = _lambda.Function(
            self,
            "MyLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("path/to/your/code"),
            function_name="my-function-name",
            vpc=my_vpc,
            security_group=my_vpc.vpc_default_security_group,
            allow_public_subnet=False,  # Set to True if you want public subnets
        )

class MySAMLambdaStack2(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a custom VPC
        my_vpc = ec2.Vpc(
            self,
            "MyVPC",
            max_azs=2,  # Set the number of Availability Zones as needed
        )

        # Define the Serverless::Function within the VPC
        my_sam_lambda_function = sam.CfnFunction(
            self,
            "MySAMLambdaFunction",
            handler="index.handler",
            runtime="nodejs14.x",
            code_uri="./my-code",
            function_name="my-function-name",
            vpc_config=sam.CfnFunction.VpcConfigProperty(
                security_group_ids=[my_vpc.vpc_default_security_group],
                subnet_ids=my_vpc.select_subnets(
                    subnet_group_name="your-subnet-group-name"
                ).subnet_ids,
            ),
        )

