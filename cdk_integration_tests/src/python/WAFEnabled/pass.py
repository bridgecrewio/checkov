from aws_cdk import core
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_wafv2 as wafv2

class CloudFrontDistributionStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a WebACL
        web_acl = wafv2.CfnWebACL(
            self,
            "MyWebACL",
            default_action={
                "allow": {}
            },
            # Configure your WebACL as needed
        )

        # Create a CloudFront distribution
        distribution = cloudfront.CfnDistribution(
            self,
            "MyCloudFrontDistribution",
            distribution_config={
                "defaultCacheBehavior": {
                    # Configure your cache behavior as needed
                },
                "enabled": True,
                "webAclId": web_acl.attr_arn  # Set the WebACL association
            }
        )

app = core.App()
CloudFrontDistributionStack(app, "CloudFrontDistributionStack")
app.synth()
