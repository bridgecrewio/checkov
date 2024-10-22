import * as cdk from 'aws-cdk-lib';
import { Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class exampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const fail = new Bucket(this, 'example', {});

    const fail2 = new Bucket(this, 'example', {
      encryption: BucketEncryption.UNENCRYPTED
    });

    const fail3 = new Bucket(this, 'example', {
      encryption: BucketEncryption.S3_MANAGED
    });
  }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
