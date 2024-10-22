from aws_cdk import core
from aws_cdk import aws_amazonmq as amazonmq

class AmazonMQStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Amazon MQ broker with PubliclyAccessible set to false
        amazonmq_broker = amazonmq.CfnBroker(
            self,
            "MyAmazonMQBroker",
            broker_name="my-amazon-mq-broker",
            engine_type="ACTIVEMQ",
            host_instance_type="mq.t2.micro",
            publicly_accessible=True,  # Set PubliclyAccessible to false
        )

app = core.App()
AmazonMQStack(app, "AmazonMQStack")
app.synth()
