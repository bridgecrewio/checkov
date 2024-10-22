from aws_cdk import core
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_sam as sam
class MyApiGatewayStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an API Gateway stage with cache cluster enabled
        api = apigateway.RestApi(
            self,
            "MyApi",
            rest_api_name="MyApiName",
        )

        stage = apigateway.Stage(
            self,
            "MyApiStage",
            stage_name="prod",  # Replace with your desired stage name
            deployment=api.latest_deployment,
        )

class MySAMApiStack2(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Serverless API with cache cluster enabled
        sam_api = sam.CfnApi(
            self,
            "MySAMApi",
            stage_name="prod",  # Specify the stage name
            definition_body={
                "openapi": "3.0.1",
                "info": {
                    "title": "MyAPI",
                },
                "paths": {
                    "/example": {
                        "get": {
                            "responses": {
                                "200": {
                                    "description": "A sample response",
                                },
                            },
                        },
                    },
                },
            },
        )
