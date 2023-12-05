from aws_cdk import core
from aws_cdk import aws_workspaces as workspaces

class WorkSpacesStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a WorkSpaces directory
        directory = workspaces.CfnWorkspaceDirectory(
            self, "MyWorkspaceDirectory",
            directory_name="my-workspace-directory",
            subnet_ids=["subnet-12345678"],  # Replace with your subnet IDs
            self_service_permissions="ENABLED",
        )

        # Create a WorkSpaces workspace with root volume encryption enabled
        workspace = workspaces.CfnWorkspace(
            self, "MyWorkspace",
            bundle_id="wsb-12345678",  # Replace with your bundle ID
            user_name="my-user",
            root_volume_encryption_enabled=False,
            user_volume_encryption_enabled=False,
            workspace_properties={"directoryId": directory.ref},
        )

app = core.App()
WorkSpacesStack(app, "WorkSpacesStack")
app.synth()
