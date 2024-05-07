import { App, Stack } from 'aws-cdk-lib';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

class MySecretsStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define a SecretsManager secret with KMS key ID
    const mySecret = new secretsmanager.Secret(this, 'MySecret', {
      secretName: 'MySecretName',
      encryptionKey: kms.Key.fromKeyArn(this, 'MyKmsKey', 'arn:aws:kms:REGION:ACCOUNT_ID:key/KMS_KEY_ID'),
    });
  }
}


const app = new App();
new MySecretsStack(app, "MySecretsStack");
app.synth();
