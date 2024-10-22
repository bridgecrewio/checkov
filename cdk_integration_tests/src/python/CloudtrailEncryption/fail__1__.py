from aws_cdk import core
from aws_cdk import aws_cloudtrail as cloudtrail

class MyCloudTrailTrailStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudTrail Trail with a specific KMS Key ID
        cloudtrail.CfnTrail(
            self, 'MyCloudTrail',
        )

app = core.App()
MyCloudTrailTrailStack(app, "MyCloudTrailTrailStack")
app.synth()
