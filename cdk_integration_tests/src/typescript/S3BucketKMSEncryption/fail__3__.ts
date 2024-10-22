import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class exampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const fail = new s3.Bucket(this, 'example', {});

    const fail2 = new s3.Bucket(this, 'example', {
      encryption: s3.BucketEncryption.UNENCRYPTED
    });

    const fail3 = new s3.Bucket(this, 'example', {
      encryption: s3.BucketEncryption.S3_MANAGED
    });
  }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
