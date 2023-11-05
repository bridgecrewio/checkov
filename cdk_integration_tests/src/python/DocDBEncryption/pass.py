from aws_cdk import core
from aws_cdk import aws_docdb as docdb

class MyDocDBClusterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Amazon DocumentDB cluster with storage encryption enabled
        docdb_cluster = docdb.CfnDBCluster(
            self,
            "MyDocDBCluster",
            db_cluster_identifier="my-docdb-cluster",
            master_username="admin",
            master_user_password="mypassword", # checkov:skip=CKV_SECRET_6 test secret
            storage_encrypted=True,  # Enable storage encryption
            availability_zones=["us-east-1a", "us-east-1b"],  # Specify the availability zones
            port=27017,  # Specify the port as needed
        )
