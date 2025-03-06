import aws_cdk as core
from constructs import Construct
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2

class MyECSClusterStack(core.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc",
            ip_protocol=ec2.IpProtocol.DUAL_STACK
        )

        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc, container_insights=True)
        cluster2 = ecs.Cluster(self, "EcsCluster2", vpc=vpc, container_insights_v2=ecs.ContainerInsights.ENHANCED)
        cluster3 = ecs.Cluster(self, "EcsCluster3", vpc=vpc, container_insights_v2=ecs.ContainerInsights.ENABLED)

        cluster4 = ecs.CfnCluster(
            self, 'MyECSCluster4',
            cluster_name='my-ecs-cluster',
            cluster_settings=[{
                'name': 'containerInsights',
                'value': 'enabled'
            }]
            # Other properties for your ECS Cluster
        )

        cluster5 = ecs.CfnCluster(
            self, 'MyECSCluster5',
            cluster_name='my-ecs-cluster',
            cluster_settings=[{
                'name': 'containerInsights',
                'value': 'enhanced'
            }]
            # Other properties for your ECS Cluster
        )

app = core.App()
MyECSClusterStack(app, "MyECSClusterStack")
app.synth()
