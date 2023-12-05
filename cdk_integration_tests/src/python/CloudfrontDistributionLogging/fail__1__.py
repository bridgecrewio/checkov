from aws_cdk import core
from aws_cdk import aws_cloudfront as cloudfront

class MyCloudFrontDistributionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudFront Distribution with logging settings
        distribution = cloudfront.CfnDistribution(
            self, 'MyCloudFrontDistribution',
        )

app = core.App()
MyCloudFrontDistributionStack(app, "MyCloudFrontDistributionStack")
app.synth()
