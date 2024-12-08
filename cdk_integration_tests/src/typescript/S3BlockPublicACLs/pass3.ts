import * as cdk from 'aws-cdk-lib';
import { Stack, App } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

const app = new App();
const stack = new Stack(app, 'S3BucketStack');

// Create an S3 bucket with blockPublicAcls enabled
const bucket = new s3.CfnBucket(stack, 'MyBucket', {
  bucketName: 'my-bucket-name', // Optional: Specify a bucket name
  versioningConfiguration: {
    status: 'Enabled',
  },
  publicAccessBlockConfiguration: {
    blockPublicAcls: true, // Only block public ACLs
    ignorePublicAcls: true,
  },
});

// Add deletion policy to the bucket
bucket.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY); // NOT recommended for production code

app.synth();
