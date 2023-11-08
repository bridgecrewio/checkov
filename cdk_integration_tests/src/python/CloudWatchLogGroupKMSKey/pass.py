from aws_cdk import core
from aws_cdk import aws_logs as logs

class MyLogGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CloudWatch Logs log group with KMS key ID
        log_group = logs.LogGroup(
            self,
            "MyLogGroup",
            log_group_name="MyLogGroupName",
            retention=logs.RetentionDays.ONE_MONTH,  # Set the retention policy as needed
            kms_key=1,  # Specify the KMS key
        )
