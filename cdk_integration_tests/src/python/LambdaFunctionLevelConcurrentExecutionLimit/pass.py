from aws_cdk import core
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_sam import CfnFunction

class MyLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        my_lambda_function = Function(
            self,
            "MyLambdaFunction",
            runtime=Runtime.PYTHON_3_8,  # Set the Lambda function's runtime
            handler="index.handler",  # Specify the Lambda handler
            code=Code.from_asset("path/to/your/code"),  # Define the code location
            function_name="my-function-name",  # Optionally set the function name
            role=my_lambda_execution_role,  # Provide an IAM role for the function
            timeout=core.Duration.seconds(10),  # Set the function timeout
            reserved_concurrent_executions=5
        )
class MyLambdaStack2(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        my_lambda_function = CfnFunction(
            self,
            "MyLambdaFunction",
            handler="index.handler",  # Specify the Lambda handler
            runtime="nodejs14.x",  # Set the Lambda function's runtime
            code_uri="./my-code",  # Specify the location of your code
            function_name="my-function-name",  # Optionally set the function name
            role=my_lambda_execution_role,  # Provide an IAM role for the function
            timeout=10,  # Set the function timeout
            reserved_concurrent_executions=5
        )

        # You can add other configurations and permissions for your Lambda function here

