from aws_cdk import core
from aws_cdk import aws_cloudtrail as cloudtrail

class MyCloudTrailStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudTrail Trail with IsMultiRegionTrail set to true
        cloudtrail.Trail(
            self, 'MyCloudTrail',
            is_multi_region_trail=False,
            # Other properties as needed for your CloudTrail Trail
        )

app = core.App()
MyCloudTrailStack(app, "MyCloudTrailStack")
app.synth()
