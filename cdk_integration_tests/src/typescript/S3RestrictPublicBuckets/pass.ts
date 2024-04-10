import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';

class S3BucketWithPublicAccessStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        new s3.Bucket(this, 'aaa', {
            versioned: false, // You can enable versioning if needed
            removalPolicy: cdk.RemovalPolicy.DESTROY, // Change this according to your retention policy
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL, // Enforce all public access restrictions
        });
    }
}

class PublicS3BucketStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        new s3.CfnBucket(this, 'PublicBucket', {
            versioningConfiguration: {
                status: 'Suspended', // You can enable versioning if needed
            },
            publicAccessBlockConfiguration: {
                blockPublicAcls: true,
                blockPublicPolicy: true,
                ignorePublicAcls: true,
                restrictPublicBuckets: true,
      },
    });
  }
}

const app = new cdk.App();
new S3BucketWithPublicAccessStack(app, 'S3BucketWithPublicAccessStack');
new PublicS3BucketStack(app, 'PublicS3BucketStack');
app.synth();