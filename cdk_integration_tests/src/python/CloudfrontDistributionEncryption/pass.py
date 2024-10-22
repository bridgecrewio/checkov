from aws_cdk import core
from aws_cdk import aws_cloudfront as cloudfront

class MyCloudFrontDistributionStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudFront Distribution with ViewerProtocolPolicy set to allow_all
        distribution = cloudfront.CfnDistribution(
            self, 'MyCloudFrontDistribution',
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                default_cache_behavior=cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    viewer_protocol_policy='abc'
                ),
                # Add other properties for the distribution config as needed
            )
        )

app = core.App()
MyCloudFrontDistributionStack(app, "MyCloudFrontDistributionStack")
app.synth()

class MyCloudFrontDistributionStack2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudFront Distribution with CacheBehavior and ViewerProtocolPolicy
        distribution = cloudfront.CfnDistribution(
            self, 'MyCloudFrontDistribution',
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                cache_behaviors=[
                    cloudfront.CfnDistribution.CacheBehaviorProperty(
                        path_pattern='/path-to-cache',
                        target_origin_id='my-target-origin-id',
                    )
                ],
                # Other distribution configuration properties
            )
        )

app = core.App()
MyCloudFrontDistributionStack2(app, "MyCloudFrontDistributionStack2")
app.synth()
