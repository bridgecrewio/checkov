from aws_cdk import core
from aws_cdk import aws_cloudtrail as cloudtrail

class MyCloudTrailTrailStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudTrail Trail with a specific KMS Key ID
        cloudtrail.CfnTrail(
            self, 'MyCloudTrail',
            kms_key_id='arn:aws:kms:REGION:ACCOUNT_ID:key/KMS_KEY_ID',  # Replace with your KMS Key ID ARN
            # Other properties for your CloudTrail Trail
        )

app = core.App()
MyCloudTrailTrailStack(app, "MyCloudTrailTrailStack")
app.synth()
