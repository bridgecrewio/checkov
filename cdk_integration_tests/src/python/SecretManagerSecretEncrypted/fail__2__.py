from aws_cdk import core
from aws_cdk import aws_secretsmanager as secretsmanager

class MySecretsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define a SecretsManager secret with KMS key ID containing "aws/"
        my_secret = secretsmanager.Secret(
            self, 'MySecret',
            secret_name='MySecretName',
            kms_key_id='arn:aws:kms:REGION:ACCOUNT_ID:key/aws/KMS_KEY_ID'
        )

class MySecretsStack2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        my_secret = secretsmanager.Secret(
            self, 'MySecret',
            secret_name='MySecretName',
        )

app = core.App()
MySecretsStack(app, "MySecretsStack")
app.synth()
