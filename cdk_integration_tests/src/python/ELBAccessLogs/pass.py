from aws_cdk import core
from aws_cdk import aws_elasticloadbalancing as elb

class MyLoadBalancerStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elastic Load Balancer with access logging policy enabled
        load_balancer = elb.CfnLoadBalancer(
            self, 'MyLoadBalancer',
            listeners=[
                {
                    'instancePort': '80',
                    'instanceProtocol': 'HTTP',
                    'loadBalancerPort': '80',
                    'protocol': 'HTTP'
                }
            ],
            access_logging_policy=elb.CfnLoadBalancer.AccessLoggingPolicyProperty(
                enabled=True,
                s3_bucket_name='my-access-logs-bucket',  # Replace with your S3 bucket name
                emit_interval=5  # Adjust the interval as needed
            )
            # Other properties as needed for your Load Balancer
        )

app = core.App()
MyLoadBalancerStack(app, "MyLoadBalancerStack")
app.synth()
