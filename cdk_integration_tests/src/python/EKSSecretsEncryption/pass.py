from aws_cdk import core
from aws_cdk import aws_eks as eks

class MyEKSClusterStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define EKS Cluster with Encryption Configuration
        cluster = eks.CfnCluster(
            self, 'MyEKSCluster',
            name='my-eks-cluster',
            encryption_config=[{
                'resources': ['secrets']
            }]
            # Other properties for your EKS Cluster
        )

app = core.App()
MyEKSClusterStack(app, "MyEKSClusterStack")
app.synth()
