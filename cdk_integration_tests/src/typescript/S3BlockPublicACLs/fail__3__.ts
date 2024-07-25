import * as cdk from 'aws-cdk-lib';
import { Stack, App } from 'aws-cdk-lib';
import { Bucket, BlockPublicAccess } from 'aws-cdk-lib/aws-s3';

const app = new App();
const stack = new Stack(app, 'S3BucketStack');

// Create an S3 bucket with blockPublicAcls enabled
const bucket = new Bucket(stack, 'MyBucket', {
    blockPublicAccess: BlockPublicAccess.IGNORE_ACLS,
    versioned: true,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
    autoDeleteObjects: true,
});

const bucket2 = new Bucket(stack, 'MyBucket', {
    versioned: true,
    removalPolicy: cdk.RemovalPolicy.DESTROY,
    autoDeleteObjects: true,
});

app.synth();

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
        blockPublicAcls: false, // Only block public ACLs
        ignorePublicAcls: true,
    },
});

bucket.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);

app.synth();

