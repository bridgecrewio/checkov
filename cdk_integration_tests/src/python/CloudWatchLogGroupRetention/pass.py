from aws_cdk import core
from aws_cdk import aws_logs as logs

class MyLogGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define CloudWatch Logs Log Group with Retention Period
        logs.CfnLogGroup(
            self, 'MyLogGroup',
            log_group_name='my-log-group',
            retention_in_days=30  # Replace with your desired retention period in days
            # Other properties for your Log Group
        )

app = core.App()
MyLogGroupStack(app, "MyLogGroupStack")
app.synth()
