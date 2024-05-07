import { App, Stack } from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as cfn from 'aws-cdk-lib/aws-cloudformation';
import { Construct } from 'constructs';

class SqsQueueWithKmsKeyStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Create a KMS key for encryption
    const kmsKey = new kms.Key(this, 'MyKmsKey', {
      enableKeyRotation: true,
    });

    // Create an SQS queue with KMS encryption
    new sqs.Queue(this, 'MySqsQueue', {
      encryption: sqs.QueueEncryption.KMS,
      encryptionMasterKey: kmsKey,
      visibilityTimeout: cdk.Duration.seconds(300), // Other properties for the queue
    });
  }
}

const app = new App();
new SqsQueueWithKmsKeyStack(app, 'SqsQueueWithKmsKeyStack');
app.synth();


class SqsQueueWithKmsKeyIdStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define a custom KMS key
    const kmsKey = new cfn.CfnCustomResource(this, 'MyKmsKeyResource', {
      serviceToken: 'arn:aws:lambda:<your-region>:<your-account>:function/<your-lambda-function>',
      // Add other properties as needed
    });

    // Define an SQS queue with a specific KmsMasterKeyId
    new sqs.CfnQueue(this, 'MySqsQueue', {
      kmsMasterKeyId: kmsKey.getAtt('KmsKeyId').toString(),
      visibilityTimeout: 300, // Other properties for the queue
    });
  }
}

const app2 = new App();
new SqsQueueWithKmsKeyIdStack(app2, 'SqsQueueWithKmsKeyIdStack');
app2.synth();
