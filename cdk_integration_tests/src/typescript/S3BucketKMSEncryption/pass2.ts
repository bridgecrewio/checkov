import * as cdk from 'aws-cdk-lib';
import { Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class exampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pass = new Bucket(this, 'example', {
      encryption: BucketEncryption.KMS
    });
  }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
