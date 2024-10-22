from aws_cdk import core
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

class MyListenerStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define HTTPS Redirect Listener
        listener = elbv2.CfnListener(
            self, 'MyHTTPSRedirectListener',
            load_balancer_arn='your-load-balancer-arn',  # Replace with your ALB ARN
            protocol='HTTP',
            port=80,
            default_actions=[{
                'type': 'abc',
                'redirectConfig': {
                    'protocol': 'HTTP',
                }
            }]
            # Other properties for your Redirect Listener
        )

app = core.App()
MyListenerStack(app, "MyListenerStack")
app.synth()
