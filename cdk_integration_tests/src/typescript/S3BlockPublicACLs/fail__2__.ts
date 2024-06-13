// FINDING
import { Bucket } from '@aws-cdk/aws-s3';

// SINK
// SINK: Vulnerability found due to S3 bucket missing block public ACLs
new Bucket(stack, 'MyBucket', {
    blockPublicAcls: false, // This should be 'true' to block public ACLs
});
new Bucket(stack, 'MyBucket', {
    random_param: 'true'
});