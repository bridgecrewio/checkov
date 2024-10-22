import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';

class S3BucketExampleStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        // Bucket with PUBLIC_READ access - Match
        new s3.Bucket(this, 'MyPublicReadBucket');

        new s3.Bucket(this, 'MyPrivateReadBucket');

        // Bucket with PUBLIC_READ_WRITE access
        new s3.Bucket(this, 'MyPublicReadWriteBucket', {
            accessControl: s3.BucketAccessControl.Private,
        });

        // Bucket with publicReadAccess set to true
        new s3.Bucket(this, 'MyPublicReadAccessBucket', {});

        // Bucket with publicReadAccess set to true
        new s3.Bucket(this, 'MyPublicReadAccessBucket', {
            publicReadAccess: false,
        });
    }
}

const app = new App();
new S3BucketExampleStack(app, 'S3BucketExampleStack');
