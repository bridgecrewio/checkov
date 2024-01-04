from aws_cdk import core
from aws_cdk import aws_apigatewayv2 as apigatewayv2

class MyApiGatewayV2StageStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define API Gateway V2 Stage with AccessLogSettings/DestinationArn set
        api_stage = apigatewayv2.CfnStage(
            self, 'MyApiGatewayV2Stage',
            api_id='api_id_here',  # Replace with your API ID
            stage_name='myStage',
            # Add other properties as needed for your stage
        )

app = core.App()
MyApiGatewayV2StageStack(app, "MyApiGatewayV2StageStack")
app.synth()

from aws_cdk import core
from aws_cdk import aws_apigatewayv2 as apigatewayv2

class MyServerlessHttpApiStack2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define a Serverless HTTP API with access log settings
        serverless_api = apigatewayv2.CfnApi(
            self, 'MyServerlessHttpApi',
            name='MyHTTPAPI',
            protocol_type='HTTP',
            # Add other properties as needed for your HTTP API
        )

app = core.App()
MyServerlessHttpApiStack2(app, "MyServerlessHttpApiStack2")
app.synth()
