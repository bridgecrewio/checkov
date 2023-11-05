from aws_cdk import core
from aws_cdk import aws_neptune as neptune

class MyNeptuneStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Neptune DB cluster with storage encryption enabled
        neptune_cluster = neptune.CfnDBCluster(
            self,
            "MyNeptuneCluster",
            engine="neptune",
            db_cluster_identifier="my-neptune-cluster",
            master_username="admin",
            master_user_password="mypassword", # checkov:skip=CKV_SECRET_6 test secret
            storage_encrypted=True,  # Enable storage encryption
            port=8182,  # Specify the port as needed
            availability_zones=["us-east-1a", "us-east-1b"],  # Specify the availability zones
        )

class MyNeptuneStack2(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Neptune DB cluster with storage encryption enabled
        neptune_cluster = neptune.DatabaseCluster(
            self,
            "MyNeptuneCluster",
            engine=neptune.DatabaseClusterEngine.NEPTUNE,
            master_user=neptune.Login(
                username="admin",
                password="mypassword", # checkov:skip=CKV_SECRET_6 test secret
            ),
            default_database_name="mydb",
            storage_encrypted=True,  # Enable storage encryption
            removal_policy=core.RemovalPolicy.DESTROY,  # Set the removal policy as needed
            vpc=your_vpc,  # Specify the VPC where the cluster should be deployed
            instances=1,  # Specify the number of instances
        )

