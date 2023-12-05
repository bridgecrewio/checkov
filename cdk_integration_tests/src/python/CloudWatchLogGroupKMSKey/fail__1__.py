from aws_cdk import core
from aws_cdk import aws_logs as logs

class MyBadLogGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CloudWatch Logs log group without specifying KMS key
        log_group = logs.LogGroup(
            self,
            "MyBadLogGroup",
            log_group_name="MyLogGroupName",
            retention=logs.RetentionDays.ONE_MONTH,  # Set the retention policy as needed
            # KMS key is not specified
        )
