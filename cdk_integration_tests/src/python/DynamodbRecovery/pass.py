from aws_cdk import core
from aws_cdk import aws_dynamodb as dynamodb

class MyDynamoDBStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a DynamoDB table with PointInTimeRecoveryEnabled set to True
        dynamodb_table = dynamodb.Table(
            self,
            "MyDynamoDBTable",
            table_name="MyTableName",
            partition_key=dynamodb.Attribute(name="PartitionKey", type=dynamodb.AttributeType.STRING),
            point_in_time_recovery=True,  # Set PointInTimeRecoveryEnabled to True
            removal_policy=core.RemovalPolicy.DESTROY,  # Specify the removal policy as needed
        )
