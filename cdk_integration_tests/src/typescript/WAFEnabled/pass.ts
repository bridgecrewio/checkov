import { App, Stack } from 'aws-cdk-lib';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import { Construct } from 'constructs';

class CloudFrontDistributionStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Create a WebACL
    const webAcl = new wafv2.CfnWebACL(this, 'MyWebACL', {
      defaultAction: { allow: {} },
      scope: 'CLOUDFRONT',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: 'webAclMetric',
        sampledRequestsEnabled: true,
      },
      // Configure your WebACL as needed
      rules: [],
    });

    // Create a CloudFront distribution
    const distribution = new cloudfront.CfnDistribution(this, 'MyCloudFrontDistribution', {
      distributionConfig: {
        defaultCacheBehavior: {
          // Configure your cache behavior as needed
          viewerProtocolPolicy: 'allow-all', // Example configuration
          targetOriginId: 'myTargetOrigin', // Example configuration, needs to match an origin
          forwardedValues: {
            queryString: false,
            cookies: { forward: 'none' },
          },
        },
        enabled: true,
        webAclId: webAcl.attrArn, // Set the WebACL association
        // Other distributionConfig properties as needed
      },
    });
  }
}

const app = new App();
new CloudFrontDistributionStack(app, 'CloudFrontDistributionStack');
app.synth();
