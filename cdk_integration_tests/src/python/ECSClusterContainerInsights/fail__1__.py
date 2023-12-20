from aws_cdk import core
from aws_cdk import aws_ecs as ecs

class MyECSClusterStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define ECS Cluster with Cluster Settings
        cluster = ecs.CfnCluster(
            self, 'MyECSCluster',
            cluster_name='my-ecs-cluster',
            cluster_settings=[{
                'name': 'containerInsights',
                'value': 'disabled'
            }]
            # Other properties for your ECS Cluster
        )

app = core.App()
MyECSClusterStack(app, "MyECSClusterStack")
app.synth()
