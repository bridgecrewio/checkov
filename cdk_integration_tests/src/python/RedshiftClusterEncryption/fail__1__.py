from aws_cdk import core
from aws_cdk import aws_redshift as redshift

class RedshiftClusterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Amazon Redshift cluster
        redshift_cluster = redshift.CfnCluster(
            self,
            "MyRedshiftCluster",
            cluster_identifier="my-redshift-cluster",
            master_username="admin",
            master_user_password="MySecurePassword123",  # checkov:skip=CKV_SECRET_6 test secret
            node_type="dc2.large",
            cluster_type="single-node",
        )

app = core.App()
RedshiftClusterStack(app, "RedshiftClusterStack")
app.synth()
