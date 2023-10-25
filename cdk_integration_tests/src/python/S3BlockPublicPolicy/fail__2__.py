from constructs import Construct
from aws_cdk import App, Stack 
from aws_cdk import (
    aws_s3 as s4
)

class MyS3Stack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s4.Bucket(self, "MyBlockedBucket",
            block_public_access=s4.BlockPublicAccess(block_public_policy=False)
        )

        bucket2 = s4.Bucket(self, "MyBlockedBucket2"
        )

app = App()
MyS3Stack(app, "MyS3Stack")
app.synth()
