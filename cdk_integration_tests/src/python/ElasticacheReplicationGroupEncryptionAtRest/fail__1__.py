from aws_cdk import core
from aws_cdk import aws_elasticache as elasticache

class ElastiCacheReplicationGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Amazon ElastiCache replication group
        replication_group = elasticache.CfnReplicationGroup(
            self,
            "MyElastiCacheReplicationGroup",
            replication_group_description="My Replication Group",
            automatic_failover_enabled=True,
            replication_group_id="my-replication-group",
            cache_node_type="cache.m4.large",
            engine="redis",
            engine_version="5.0.6",
            num_node_groups=2,
            cache_subnet_group_name="my-subnet-group",
            security_group_ids=["sg-0123456789abcdef0"],
        )

app = core.App()
ElastiCacheReplicationGroupStack(app, "ElastiCacheReplicationGroupStack")
app.synth()
