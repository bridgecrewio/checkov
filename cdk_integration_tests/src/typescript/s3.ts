import { App, Stack, StackProps } from "aws-cdk-lib";
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class exampleStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    new s3.Bucket(this, 'example', {
      encryption: s3.BucketEncryption.S3_MANAGED,
    });
  }
}

const app = new App();
new exampleStack(app, 'example-stack');
app.synth();
