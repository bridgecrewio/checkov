from constructs import Construct
from aws_cdk import App, Stack 
from aws_cdk import (
    aws_s3 as s4
)

class MyStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

		# fail
        bucket = s4.Bucket(self, "MyS3Bucket",
            bucket_name='my-s3-bucket',
            public_read_access=False,
            block_public_access=s4.BlockPublicAccess(
                ignore_public_acls=False
            )
        )

        value = False
		# fail
        bucket2 = s4.Bucket(self, "MyS3Bucket2",
            bucket_name='my-s3-bucket2',
            public_read_access=False,
            block_public_access=s4.BlockPublicAccess(
                ignore_public_acls=value
            )
        )

app = App()
MyStack(app, "my-stack-name")

app.synth()
