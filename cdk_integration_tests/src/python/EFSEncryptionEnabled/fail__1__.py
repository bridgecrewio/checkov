from aws_cdk import core
from aws_cdk import aws_efs as efs

class EfsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        efs_file_system = efs.FileSystem(
            self,
            "EfsFileSystem",
            encrypted=False,  # Set Encrypted property to False
            lifecycle_policy=efs.LifecyclePolicy.AFTER_7_DAYS,
        )

app = core.App()
EfsStack(app, "EfsStack")
app.synth()
