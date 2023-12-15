from aws_cdk import core
from aws_cdk import aws_glue as glue

class MyGlueSecurityConfigurationStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the security configuration with encryption settings
        security_configuration = glue.CfnSecurityConfiguration(
            self, 'MyGlueSecurityConfiguration',
            encryption_configuration={
                'CloudWatchEncryption': {
                    'CloudWatchEncryptionMode': 'SSE-KMS'
                },
                'JobBookmarksEncryption': {
                    'JobBookmarksEncryptionMode': 'DISABLED'
                },
                'S3Encryptions': [
                    {
                        'S3EncryptionMode': 'SSE-KMS'
                    }
                ]
            }
        )

app = core.App()
MyGlueSecurityConfigurationStack(app, "MyGlueSecurityConfigurationStack")
app.synth()

class MyGlueSecurityConfigurationStack2(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the security configuration with encryption settings
        security_configuration = glue.CfnSecurityConfiguration(
            self, 'MyGlueSecurityConfiguration',
            encryption_configuration={
                'JobBookmarksEncryption': {
                    'JobBookmarksEncryptionMode': 'CSE-KMS'
                },
                'S3Encryptions': [
                    {
                        'S3EncryptionMode': 'SSE-KMS'
                    }
                ]
            }
        )

app = core.App()
MyGlueSecurityConfigurationStack2(app, "MyGlueSecurityConfigurationStack2")
app.synth()
