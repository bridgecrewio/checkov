import * as cdk from 'aws-cdk-lib';
import { Stack, App } from 'aws-cdk-lib';
import { Bucket, BlockPublicAccess } from 'aws-cdk-lib/aws-s3';

const app = new App();
const stack = new Stack(app, 'S3BucketStack');

// Create an S3 bucket with blockPublicAcls enabled
const bucket = new Bucket(stack, 'MyBucket', {
  blockPublicAccess: BlockPublicAccess.BLOCK_ACLS, // Only block public ACLs
  versioned: true,
  removalPolicy: cdk.RemovalPolicy.DESTROY, // NOT recommended for production code
  autoDeleteObjects: true, // NOT recommended for production code
});

const bucket2 = new Bucket(stack, 'MyBucket', {
  blockPublicAccess: BlockPublicAccess.BLOCK_ALL, // Only block public ACLs
  versioned: true,
  removalPolicy: cdk.RemovalPolicy.DESTROY, // NOT recommended for production code
  autoDeleteObjects: true, // NOT recommended for production code
});

app.synth();

