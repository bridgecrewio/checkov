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
      encryptionKey: kms.Key.fromKeyArn(this, 'MyKmsKey', 'arn:aws:kms:REGION:ACCOUNT_ID:key/aws/KMS_KEY_ID'),
    });
  }
}

class MySecretsStack2 extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define a SecretsManager secret without specifying KMS key ID
    const mySecret = new secretsmanager.Secret(this, 'MySecret', {
      secretName: 'MySecretName',
    });
  }
}

const app = new App();
new MySecretsStack(app, "MySecretsStack");
new MySecretsStack2(app, "MySecretsStack2");
app.synth();
