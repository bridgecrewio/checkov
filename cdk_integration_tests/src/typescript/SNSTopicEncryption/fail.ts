import { App, Stack } from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    new sns.Topic(this, 'Topic', {
      topicName: 'my-topic',
    });
  }
}

const app = new App();
new MyStack(app, 'MyStack');
app.synth();
