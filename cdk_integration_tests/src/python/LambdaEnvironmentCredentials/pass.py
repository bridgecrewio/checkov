from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sam as sam

class MyLambdaFunctionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Lambda Function
        my_lambda = _lambda.Function(
            self, 'MyLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='index.handler',
            code=_lambda.Code.from_asset('lambda'),  # Replace 'lambda' with your function code directory
            environment={
                'MY_VARIABLE': {'a':'b'}
            }
        )

app = core.App()
MyLambdaFunctionStack(app, "MyLambdaFunctionStack")
app.synth()


class MyServerlessFunctionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Serverless Lambda Function
        my_lambda = sam.CfnFunction(
            self, 'MyServerlessFunction',
            code_uri='lambda/',  # Replace 'lambda/' with your function code directory
            handler='index.handler',
            runtime='python3.8',
            environment={
                'MY_VARIABLE': {'a':'b'}
            }
            # Other properties for your Serverless Lambda Function
        )

app = core.App()
MyServerlessFunctionStack(app, "MyServerlessFunctionStack")
app.synth()
