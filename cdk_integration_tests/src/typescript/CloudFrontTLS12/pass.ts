// Import necessary AWS CDK packages
import * as cloudfront from '@aws-cdk/aws-cloudfront';
import { Construct } from '@aws-cdk/core';

// Example of a ViewerCertificateProperty that does not specify TLS v1.2
// FINDING
const viewerCertificateConfig: cloudfront.CfnDistribution.ViewerCertificateProperty = {
  // Viewer certificate configuration details
};

// This should not match the pattern as it includes a ViewerCertificate with TLSv1.2
const distributionWithTLSv12 = new cloudfront.CfnDistribution(new Construct(), 'distributionWithTLSv12', {
  // other configuration details
  viewerCertificate: {
    minimumProtocolVersion: 'TLSv1.2' // This is the correct configuration
  }
});
