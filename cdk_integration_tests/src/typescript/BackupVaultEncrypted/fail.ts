import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class BackupVaultEncryptedStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new elbv2.CfnBackupVault(this, {})
        new elbv2.CfnBackupVault(this, {encryptionKeyArn: false})
    }
}

const app = new App();
new BackupVaultEncryptedStack(app, 'BackupVaultEncryptedStack');
