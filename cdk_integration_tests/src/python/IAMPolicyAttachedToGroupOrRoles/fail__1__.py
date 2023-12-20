from aws_cdk import core
from aws_cdk import aws_iam as iam

class IAMStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an IAM policy
        custom_policy = iam.Policy(
            self,
            "CustomPolicy",
            policy_name="MyCustomPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["s3:GetObject"],
                    resources=["arn:aws:s3:::my-bucket/*"],
                ),
            ],
            users=["a"]
        )


app = core.App()
IAMStack(app, "IAMStack")
app.synth()
