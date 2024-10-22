from aws_cdk import core
from aws_cdk import aws_cloudfront as cloudfront

class CloudFrontDistributionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CloudFront distribution
        distribution = cloudfront.CfnDistribution(
            self,
            "MyCloudFrontDistribution",
            distribution_config={
                "defaultCacheBehavior": {
                    # Configure your cache behavior as needed
                },
                "enabled": True,
            }
        )

app = core.App()
CloudFrontDistributionStack(app, "CloudFrontDistributionStack")
app.synth()