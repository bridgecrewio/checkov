import { App, Stack } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Create a new KMS Key
    const key = new kms.Key(this, 'MyKey');

    // Create a new SNS Topic using the KMS Key for encryption
    new sns.Topic(this, 'Topic', {
      topicName: 'my-topic',
      masterKey: key,
    });
  }
}

const app = new App();
new MyStack(app, 'MyStack');
app.synth();
