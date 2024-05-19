// FINDING
import { Bucket } from '@aws-cdk/aws-s3';

// SINK
// SINK: Vulnerability found due to S3 bucket missing block public policy
new Bucket(stack, 'MyBucket', {
    publicReadAccess: true, // This should be 'false' to block public policy
});
