from aws_cdk import core
from aws_cdk import aws_rds as rds

class RDSStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an RDS DB instance with a custom MonitoringInterval
        rds_instance = rds.DatabaseInstance(
            self,
            "MyRDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0
            ),
            instance_type=core.Fn.select(0, core.Fn.split(" ", "db.m5.large")),
            allocated_storage=20,
            max_allocated_storage=100,
            vpc_subnets={
                "subnetType": core.Fn.select(0, core.Fn.split(",", "private")),
            },
            storage_type=rds.StorageType.GP2,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

app = core.App()
RDSStack(app, "RDSStack")
app.synth()
