from aws_cdk import App, Stack, aws_s3 as s3


class AppStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        fail_1 = s3.Bucket(
            self,
            "example",
        )

        fail_2 = s3.Bucket(
            self,
            "example",
            encryption=s3.BucketEncryption.UNENCRYPTED,
        )

        fail_3 = s3.Bucket(
            self,
            "example",
            encryption=s3.BucketEncryption.S3_MANAGED,
        )


app = App()
AppStack(app, "example-stack")
app.synth()
