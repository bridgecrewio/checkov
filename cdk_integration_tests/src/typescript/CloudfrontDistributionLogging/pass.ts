import * as cdk from 'aws-cdk-lib';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as logs from 'aws-cdk-lib/aws-logs';

export class CloudFrontStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket for storing CloudFront access logs
    const logBucket = new s3.Bucket(this, 'LogBucket');

    // Creating an origin for the CloudFront distribution
    const myOrigin = new cloudfront.Origins.S3Origin({ domainName: 'my-bucket.s3.amazonaws.com' });

    // Creating a CloudFront distribution using the Distribution construct
    const distribution = new cloudfront.Distribution(this, 'MyDistribution', {
      defaultBehavior: {
        origin: myOrigin,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.ALLOW_ALL,
      },
      enableLogging: true, // Enable access logging
      logBucket: logBucket,
      logFilePrefix: 'cf-access-logs/', // Optional: prefix for log file names
    });

    // Optionally grant CloudFront permission to write access logs to the S3 bucket
    logBucket.grantWrite(distribution.logBucketDelivery);
  }
}

// Example usage
const app = new cdk.App();
new CloudFrontStack(app, 'CloudFrontStack');

export class CloudFrontStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket for storing CloudFront access logs
    const logBucket = new s3.Bucket(this, 'LogBucket');

    // Creating an origin for the CloudFront distribution
    const myOrigin = new cloudfront.CfnDistribution.OriginProperty({
      domainName: 'my-bucket.s3.amazonaws.com',
      id: 'myOrigin',
      s3OriginConfig: {},
    });

    // Creating a CloudFront distribution using the CfnDistribution construct
    const distribution = new cloudfront.CfnDistribution(this, 'MyDistribution', {
      distributionConfig: {
        defaultCacheBehavior: {
          targetOriginId: 'myOrigin',
          viewerProtocolPolicy: 'allow-all',
        },
        origins: [myOrigin],
        enabled: true,
        logging: {
          bucket: logBucket.bucketName,
          prefix: 'cf-access-logs/', // Optional: prefix for log file names
          includeCookies: false, // Optional: whether to include cookies in access logs
        },
      },
    });

    // Optionally grant CloudFront permission to write access logs to the S3 bucket
    logBucket.grantWrite(distribution.logBucketDeliveryWrite);
  }
}

// Example usage
const app = new cdk.App();
new CloudFrontStack(app, 'CloudFrontStack');
