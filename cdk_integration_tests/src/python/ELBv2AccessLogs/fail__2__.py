from aws_cdk import core
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

class MyALBWithAccessLogs(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elastic Load Balancer V2 with access logs enabled
        alb = elbv2.CfnLoadBalancer(
            self, 'MyALB',
            load_balancer_attributes=[
                elbv2.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key="access_logs.s3.enabled",
                    value="false"
                )
            ],
            # Other properties for your Application Load Balancer
        )

app = core.App()
MyALBWithAccessLogs(app, "MyALBWithAccessLogs")
app.synth()

class MyALBWithAccessLogs2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elastic Load Balancer V2 with access logs enabled
        alb = elbv2.CfnLoadBalancer(
            self, 'MyALB'
        )

app = core.App()
MyALBWithAccessLogs2(app, "MyALBWithAccessLogs2")
app.synth()
