from aws_cdk import App, Stack, aws_s3


class AppStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        bucket = aws_s3.Bucket(
            self,
            "example",
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
        )


app = App()
AppStack(app, "example-stack")
app.synth()
