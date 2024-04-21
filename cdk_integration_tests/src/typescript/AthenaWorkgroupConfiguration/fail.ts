// Import necessary AWS CDK packages
import * as athena from '@aws-cdk/aws-athena';

// Example of a Workgroup configuration
// FINDING
const workgroupConfig: athena.CfnWorkGroup.WorkGroupConfigurationProperty = {
  // Workgroup configuration details
};

// This should match the pattern and be flagged as a vulnerability
// SINK
const workgroupWithoutEnforcement = new athena.CfnWorkGroup(this, 'workgroupWithoutEnforcement', {
  // other configuration details
  workGroupConfiguration: {
    // Workgroup configuration details without enforceWorkGroupConfiguration
  }
});

const workgroupWithoutEnforcement2 = new athena.CfnWorkGroup(this, 'workgroupWithoutEnforcement', {
  // other configuration details
  workGroupConfiguration: workgroupConfig
});

// The SAST engine should flag 1 vulnerability: `workgroupWithoutEnforcement`.
