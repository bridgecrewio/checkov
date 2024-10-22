from aws_cdk import core
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_apigatewayv2 as apigatewayv2

class MyApiGatewayStageStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define API Gateway Stage with Tracing Enabled
        apigateway.CfnStage(
            self, 'MyApiGatewayStage',
            stage_name='my-stage',
            rest_api_id='your-rest-api-id',  # Replace with your RestApi Id
            tracing_enabled=False
            # Other properties for your API Gateway Stage
        )

app = core.App()
MyApiGatewayStageStack(app, "MyApiGatewayStageStack")
app.synth()

class MyServerlessApiStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Serverless API with Tracing Enabled
        api = apigatewayv2.CfnApi(
            self, 'MyServerlessApi',
            name='my-serverless-api',
            protocol_type='HTTP'
            # Other properties for your Serverless API
        )

        stage = apigatewayv2.CfnStage(
            self, 'MyServerlessApiStage',
            api_id=api.ref,
            stage_name='my-stage',
            tracing_enabled=False
            # Other properties for your API Gatewayv2 Stage
        )

app = core.App()
MyServerlessApiStack(app, "MyServerlessApiStack")
app.synth()