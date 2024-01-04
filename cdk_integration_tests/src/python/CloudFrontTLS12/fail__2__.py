from aws_cdk import core
from aws_cdk import aws_cloudfront as cloudfront

class MyCloudFrontDistributionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        distribution = cloudfront.CfnDistribution(
            self, 'MyCloudFrontDistribution',
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                viewer_certificate=cloudfront.CfnDistribution.ViewerCertificateProperty(
                    cloudfront_default_certificate=False,
                    minimum_protocol_version='TLSv1.1'  # Define the minimum supported TLS version
                ),
                # Other distribution configuration properties
            )
        )

app = core.App()
MyCloudFrontDistributionStack(app, "MyCloudFrontDistributionStack")
app.synth()

class MyCloudFrontDistributionStack2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        distribution = cloudfront.CfnDistribution(
            self, 'MyCloudFrontDistribution',
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                viewer_certificate=cloudfront.CfnDistribution.ViewerCertificateProperty(
                    cloudfront_default_certificate=False,
                    minimum_protocol_version='TLSv1.0'  # Define the minimum supported TLS version
                ),
                # Other distribution configuration properties
            )
        )

app = core.App()
MyCloudFrontDistributionStack2(app, "MyCloudFrontDistributionStack2")
app.synth()
