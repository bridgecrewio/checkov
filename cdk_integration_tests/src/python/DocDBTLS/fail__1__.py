from aws_cdk import core
from aws_cdk import aws_docdb as docdb

class MyDocDBParameterGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define DocDB Cluster Parameter Group with 'tls' parameter set to 'disabled'
        docdb.CfnDBClusterParameterGroup(
            self, 'MyDocDBClusterParameterGroup',
            description='My DocDB Parameter Group',
            family='docdb4.0',
            parameters={
                'tls': 'disabled'
            }
            # Other properties as needed
        )

app = core.App()
MyDocDBParameterGroupStack(app, "MyDocDBParameterGroupStack")
app.synth()
