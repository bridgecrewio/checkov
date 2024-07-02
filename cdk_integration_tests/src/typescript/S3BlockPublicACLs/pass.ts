// FINDING
import { Bucket } from '@aws-cdk/aws-s3';

// SINK
// SINK: Vulnerability found due to S3 bucket missing block public ACLs
new Bucket(stack, 'MyBucket', {
    blockPublicAcls: true, // This should be 'true' to block public ACLs
});
