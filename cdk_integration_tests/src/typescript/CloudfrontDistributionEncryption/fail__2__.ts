import * as cdk from 'aws-cdk-lib';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';

export class CloudFrontStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Creating an origin for the CloudFront distribution
    const myOrigin = new origins.S3Origin({ domainName: 'my-bucket.s3.amazonaws.com' });

    // Creating a CloudFront distribution
    const distribution = new cloudfront.CfnDistribution(this, 'MyDistribution', {
      distributionConfig: {
        defaultCacheBehavior: {
          targetOriginId: 'myOrigin1',
          viewerProtocolPolicy: 'allow-all',
        },
        origins: [
          {
            id: 'myOrigin1',
            domainName: 'my-bucket.s3.amazonaws.com',
            s3OriginConfig: {},
          },
        ],
        enabled: true,
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new CloudFrontStack(app, 'CloudFrontStack');


export class CloudFrontStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Creating an origin for the CloudFront distribution
    const myOrigin = new origins.S3Origin({ domainName: 'my-bucket.s3.amazonaws.com' });

    // Creating a CloudFront distribution using the Distribution construct
    const distribution = new cloudfront.Distribution(this, 'MyDistribution', {
      defaultBehavior: {
        origin: myOrigin,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.ALLOW_ALL, // Allow all protocols
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new CloudFrontStack(app, 'CloudFrontStack');

