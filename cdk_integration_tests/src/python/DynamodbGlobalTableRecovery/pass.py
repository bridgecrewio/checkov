from aws_cdk import core
from aws_cdk import aws_dynamodb as dynamodb

class DynamoDBGlobalTableStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a DynamoDB Global Table
        global_table = dynamodb.CfnGlobalTable(
            self, "MyGlobalTable",
            replication_group=[{"region_name": "us-east-1"}, {"region_name": "us-west-2"}],
            table_name="MyGlobalTable",
            replicas=[
                dynamodb.CfnGlobalTable.ReplicaSpecificationProperty(
                    point_in_time_recovery_specification=dynamodb.CfnGlobalTable.PointInTimeRecoverySpecificationProperty(
                        point_in_time_recovery_enabled=True
                    )
                )
            ]
        )