from aws_cdk import core
from aws_cdk import aws_s3 as s3

class S3BucketWithPublicAccessStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        s3.Bucket(
            self,
            "aaa",
            versioned=False,  # You can enable versioning if needed
            removal_policy=core.RemovalPolicy.DESTROY,  # Change this according to your retention policy
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=False
        )

app = core.App()
S3BucketWithPublicAccessStack(app, "S3BucketWithPublicAccessStack")
app.synth()

class PublicS3BucketStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CloudFormation S3 bucket resource
        public_bucket = s3.CfnBucket(
            self,
            "PublicBucket",
            versioning_configuration={
                "status": "Suspended"  # You can enable versioning if needed
            },
            public_access_block_configuration={
                "blockPublicAcls": True,
                "blockPublicPolicy": True,
                "ignorePublicAcls": True,
                "restrictPublicBuckets": False
            }
        )

app = core.App()
PublicS3BucketStack(app, "PublicS3BucketStack")
app.synth()

