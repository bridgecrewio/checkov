from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sam as sam
class MyLambdaFunctionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Lambda function
        my_lambda_function = _lambda.Function(
            self, 'MyLambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='index.handler',
            code=_lambda.Code.from_asset('path/to/your/function/code'),
            environment={
                'MY_VARIABLE_1': 'Value1',
                'MY_VARIABLE_2': 'Value2'
            },
            kms_key=_lambda.Key.from_key_arn(self, 'MyKmsKey', 'arn:aws:kms:region:account-id:key/key-id')
        )

app = core.App()
MyLambdaFunctionStack(app, "MyLambdaFunctionStack")
app.synth()


class MyServerlessFunctionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define SAM Function
        my_sam_function = sam.CfnFunction(
            self, 'MySAMFunction',
            handler='index.handler',
            runtime='python3.8',
            code_uri='./path/to/your/function/code',
            environment={
                'MY_VARIABLE_1': 'Value1',
                'MY_VARIABLE_2': 'Value2'
            },
            kms_key_arn='arn:aws:kms:region:account-id:key/key-id'
        )

app = core.App()
MyServerlessFunctionStack(app, "MyServerlessFunctionStack")
app.synth()
