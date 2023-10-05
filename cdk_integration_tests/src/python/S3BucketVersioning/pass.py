from aws_cdk import App, Stack, aws_s3 as s3


class AppStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        pass_1 = s3.Bucket(
            self,
            "example",
            versioned=True,
        )


app = App()
AppStack(app, "example-stack")
app.synth()
