from aws_cdk import core
from aws_cdk import aws_docdb as docdb

class DocDBStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the DocDB Cluster Parameter Group
        db_parameter_group = docdb.CfnDBClusterParameterGroup(
            self,
            "DocDBClusterParameterGroup",
            description="Custom DocDB Cluster Parameter Group",
            family="docdb4.0",
            parameters={
                "audit_logs": "enabled",
            }
        )

app = core.App()
DocDBStack(app, "DocDBStack")
app.synth()
