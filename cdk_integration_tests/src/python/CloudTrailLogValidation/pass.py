from aws_cdk import core
from aws_cdk import aws_cloudtrail as cloudtrail
from aws_cdk import aws_iam as iam

class CloudTrailStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an AWS CloudTrail trail using CfnTrail
        trail = cloudtrail.CfnTrail(
            self,
            "MyCloudTrail",
            is_logging=True,
            enable_log_file_validation=True,  # Enable log file validation
            management_events=[
                cloudtrail.ReadWriteType.WRITE_ONLY,
            ],
            include_global_service_events=True,
        )

app = core.App()
CloudTrailStack(app, "CloudTrailStack")
app.synth()
