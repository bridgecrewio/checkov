from aws_cdk import core
from aws_cdk import aws_dms as dms

class MyDMSReplicationInstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define DMS Replication Instance with PubliclyAccessible set to False
        dms.ReplicationInstance(
            self, 'MyDMSReplicationInstance',
            replication_instance_identifier='MyReplicationInstance',
            allocated_storage=100,
            engine_version='3.4.3',
            publicly_accessible=False  # Set PubliclyAccessible to False
            # Add other properties as needed for your replication instance
        )

app = core.App()
MyDMSReplicationInstanceStack(app, "MyDMSReplicationInstanceStack")
app.synth()
