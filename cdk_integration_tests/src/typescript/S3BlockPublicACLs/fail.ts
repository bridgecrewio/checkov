import * as cdk from 'aws-cdk-lib';
import { Stack, App } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

const app = new App();
const stack = new Stack(app, 'S3BucketStack');

// Create an S3 bucket with blockPublicAcls enabled
const bucket = new s3.Bucket(stack, 'MyBucket', {
    blockPublicAccess: s3.BlockPublicAccess.IGNORE_ACLS,
    versioned: true,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
    autoDeleteObjects: true,
});

app.synth();
