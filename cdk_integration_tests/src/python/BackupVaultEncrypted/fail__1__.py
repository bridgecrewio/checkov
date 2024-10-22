from aws_cdk import core
from aws_cdk import aws_backup as backup

class MyBackupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Backup Vault with the specified encryption key ARN
        backup_vault = backup.CfnBackupVault(
            self,
            "MyBackupVault",
            name="MyBackupVault",
        )
