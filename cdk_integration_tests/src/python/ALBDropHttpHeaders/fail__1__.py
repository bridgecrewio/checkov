from aws_cdk import core
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

class MyALBStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define ALB with Load Balancer Attributes
        alb = elbv2.CfnLoadBalancer(
            self, 'MyALB',
            name='my-alb',
            type='application',
            load_balancer_attributes=[
                {
                    'key': 'routing.http.drop_invalid_header_fields.enabled',
                    'value': 'false'
                }
            ]
            # Other properties for your ALB
        )

app = core.App()
MyALBStack(app, "MyALBStack")
app.synth()
