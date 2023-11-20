from aws_cdk import core
from aws_cdk import aws_elasticache as elasticache

class ElastiCacheReplicationGroupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an AWS ElastiCache Replication Group
        replication_group = elasticache.CfnReplicationGroup(
            self,
            "MyElastiCacheReplicationGroup",
            replication_group_id="my-replication-group",
            replication_group_description="My ElastiCache Replication Group",
            cache_node_type="cache.m4.large",
            engine="redis",
            engine_version="5.0.6",
            port=6379,
            num_cache_clusters=2,
            automatic_failover_enabled=True,
        )

app = core.App()
ElastiCacheReplicationGroupStack(app, "ElastiCacheReplicationGroupStack")
app.synth()
