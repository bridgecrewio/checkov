from aws_cdk import core
from aws_cdk import aws_transfer as transfer

class MyTransferServerStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Transfer Server with EndpointType set to VPC
        transfer.CfnServer(
            self, 'MyTransferServer',
            endpoint_type='abc',
            # Other properties as needed for your Transfer Server
        )

app = core.App()
MyTransferServerStack(app, "MyTransferServerStack")
app.synth()