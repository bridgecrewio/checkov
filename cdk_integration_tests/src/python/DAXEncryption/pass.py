from aws_cdk import core
from aws_cdk import aws_dax as dax

class DAXClusterStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a DAX cluster
        dax_cluster = dax.CfnCluster(
            self, "MyDAXCluster",
            cluster_name="MyDAXCluster",
            description="My DAX Cluster",
            iam_role_arn="arn:aws:iam::123456789012:role/DAXServiceRole",
            node_type="dax.r5.large",
            replication_factor=2,
            sse_specification=dax.CfnCluster.SSESpecificationProperty(
                enabled=True,  # Enable server-side encryption
                kms_key_id="arn:aws:kms:us-east-1:123456789012:key/your-kms-key-id"
            )
        )

app = core.App()
DAXClusterStack(app, "DAXClusterStack")
app.synth()
