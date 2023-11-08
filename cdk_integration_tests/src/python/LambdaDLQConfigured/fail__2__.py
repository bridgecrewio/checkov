from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_sam as sam
class MyLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the Dead Letter Queue
        dlq = sqs.Queue(
            self,
            "MyDeadLetterQueue",
            visibility_timeout=core.Duration.seconds(300),  # Adjust as needed
        )

        # Create the Lambda function with a DLQ
        my_lambda_function = _lambda.Function(
            self,
            "MyLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("path/to/your/code"),
            function_name="my-function-name",
        )



class MySAMLambdaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the Dead Letter Queue
        dlq = sqs.Queue(
            self,
            "MyDeadLetterQueue",
            visibility_timeout=core.Duration.seconds(300),  # Adjust as needed
        )

        # Create the SAM Lambda function with a DLQ
        my_sam_lambda_function = sam.CfnFunction(
            self,
            "MySAMLambdaFunction",
            handler="index.handler",
            runtime="nodejs14.x",
            code_uri="./my-code",
            function_name="my-function-name",
        )


