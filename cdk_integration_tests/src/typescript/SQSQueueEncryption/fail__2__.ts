import { App, Stack } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';

class SqsQueueWithKmsKeyStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    new sqs.Queue(this, "MySqsQueue", {
      encryption: sqs.QueueEncryption.KMS,
      visibilityTimeout: cdk.Duration.seconds(300) // Other properties for the queue
    });
  }
}

const app = new App();
new SqsQueueWithKmsKeyStack(app, "SqsQueueWithKmsKeyStack");
app.synth();

class SqsQueueWithKmsKeyIdStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    var mySqs = new sqs.CfnQueue(this, "MySqsQueue", {
      visibilityTimeout: 300  // Other properties for the queue
      // Specify the KMS key ID if needed here, e.g., kmsMasterKeyId: 'alias/aws/sqs'
    });
  }
}

const app2 = new App();
new SqsQueueWithKmsKeyIdStack(app2, "SqsQueueWithKmsKeyIdStack");
app2.synth();
