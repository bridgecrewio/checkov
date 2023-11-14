from aws_cdk import core
from aws_cdk import aws_athena as athena

class AthenaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an Athena WorkGroup
        workgroup = athena.CfnWorkGroup(
            self,
            "MyAthenaWorkGroup",
            name="my-workgroup",
            description="My Athena WorkGroup",
            state="ENABLED",  # You can change the state
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                additional_configuration="additionalConfiguration",
                bytes_scanned_cutoff_per_query=123,
                customer_content_encryption_configuration=athena.CfnWorkGroup.CustomerContentEncryptionConfigurationProperty(
                    kms_key="kmsKey"
                ),
                enforce_work_group_configuration=False,
            )
        )

app = core.App()
AthenaStack(app, "AthenaStack")
app.synth()
