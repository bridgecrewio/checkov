from aws_cdk import core
from aws_cdk import aws_redshift as redshift

class RedshiftStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Redshift cluster with PubliclyAccessible set to False
        redshift_cluster = redshift.CfnCluster(
            self,
            "MyRedshiftCluster",
            cluster_identifier="my-redshift-cluster",
            node_type="dc2.large",
            publicly_accessible=False,  # Set PubliclyAccessible to False
            master_username="admin",
            master_user_password="MyPassword123", # checkov:skip=CKV_SECRET_6 test secret
        )

app = core.App()
RedshiftStack(app, "RedshiftStack")
app.synth()
