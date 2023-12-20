from aws_cdk import core
from aws_cdk import aws_ecr as ecr

class MyECRRepositoryStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define ECR Repository with Encryption Configuration
        ecr.CfnRepository(
            self, 'MyECRRepository',
            repository_name='my-ecr-repo',
            encryption_configuration={
                'encryptionType': 'KMS'
            }
            # Other properties for your ECR Repository
        )

app = core.App()
MyECRRepositoryStack(app, "MyECRRepositoryStack")
app.synth()
