from aws_cdk import core
from aws_cdk import aws_s3 as s3

class S3BucketWithBlockPublicAclsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        s3.Bucket(
            self,
            "MyBucket",
            block_public_access=s3.BlockPublicAccess(block_public_acls=False)
        )

app = core.App()
S3BucketWithBlockPublicAclsStack(app, "S3BucketWithBlockPublicAclsStack")
app.synth()

class S3BucketWithBlockPublicAclsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        s3.CfnBucket(
            self,
            "MyBucket",
            public_access_block_configuration={
                "blockPublicAcls": False,
                "blockPublicPolicy": True,
                "ignorePublicAcls": True,
                "restrictPublicBuckets": True
            }
        )

app = core.App()
S3BucketWithBlockPublicAclsStack(app, "S3BucketWithBlockPublicAclsStack")
app.synth()
