import { App, Stack } from 'aws-cdk-lib';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import { Construct } from 'constructs';

class CloudFrontDistributionStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Create a CloudFront distribution
    new cloudfront.CfnDistribution(this, 'MyCloudFrontDistribution', {
      distributionConfig: {
        defaultCacheBehavior: {
          // Configure your cache behavior as needed
          viewerProtocolPolicy: 'allow-all', // Example configuration
          targetOriginId: 'myTargetOrigin', // Example configuration, needs to match an origin
          forwardedValues: {
            queryString: true,
            cookies: { forward: 'none' },
          },
        },
        enabled: true,
        // Other distributionConfig properties as needed
      },
    });
  }
}

const app = new App();
new CloudFrontDistributionStack(app, "CloudFrontDistributionStack");
app.synth();
