// Import necessary AWS CDK packages
import * as athena from '@aws-cdk/aws-athena';

// This should match the pattern and be flagged as a vulnerability
// SINK
const workgroupWithoutEnforcement = new athena.CfnWorkGroup(this, 'workgroupWithoutEnforcement', {
  // other configuration details
  workGroupConfiguration: {
    // Workgroup configuration details without enforceWorkGroupConfiguration
  }
});
