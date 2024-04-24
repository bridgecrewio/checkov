// Import necessary AWS CDK packages
import * as cloudfront from '@aws-cdk/aws-cloudfront';
import { Construct } from '@aws-cdk/core';

// Example of a ViewerCertificateProperty that does not specify TLS v1.2
// FINDING
const viewerCertificateConfig: cloudfront.CfnDistribution.ViewerCertificateProperty = {
  // Viewer certificate configuration details
};

// This should match the pattern and be flagged as a vulnerability
// SINK
const distributionWithoutTLSv12 = new cloudfront.CfnDistribution(new Construct(), 'distributionWithoutTLSv12', {
  // other configuration details
  viewerCertificate: {
    // Incorrect or missing minimumProtocolVersion configuration
  }
});

// The SAST engine should flag 1 vulnerability: `distributionWithoutTLSv12`.
