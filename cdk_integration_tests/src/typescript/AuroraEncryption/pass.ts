import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class AuroraEncryptionStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new elbv2.CfnDBCluster(this, {storageEncrypted: true})
    }
}

const app = new App();
new AuroraEncryptionStack(app, 'AuroraEncryptionStack');
