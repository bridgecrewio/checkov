from aws_cdk import core
from aws_cdk import aws_secretsmanager as secretsmanager

class MySecretsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define a SecretsManager secret with KMS key ID containing "aws/"
        my_secret = secretsmanager.Secret(
            self, 'MySecret',
            secret_name='MySecretName',
            kms_key_id='arn:aws:kms:REGION:ACCOUNT_ID:key/KMS_KEY_ID'
        )

app = core.App()
MySecretsStack(app, "MySecretsStack")
app.synth()
