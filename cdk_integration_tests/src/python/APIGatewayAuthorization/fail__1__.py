from aws_cdk import core
from aws_cdk import aws_apigateway as apigw

class MyApiGatewayMethodStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the API Gateway Method based on the conditions
        api_method = apigw.Method(
            self, 'MyApiGatewayMethod',
            http_method='GET',  # Replace with your desired HTTP method
            resource=self.node.try_get_context('resource'),  # Replace with your API resource
            rest_api=self.node.try_get_context('rest_api'),  # Replace with your REST API
            authorization_type=apigw.AuthorizationType.NONE,  # Set the AuthorizationType to NONE
            api_key_required=False  # Set ApiKeyRequired to false
            # You can add other properties as needed for your method
        )

app = core.App()
MyApiGatewayMethodStack(app, "MyApiGatewayMethodStack")
app.synth()
