// Import necessary AWS CDK packages
import * as athena from '@aws-cdk/aws-athena';

// Example of a Workgroup configuration
// FINDING
const workgroupConfig: athena.CfnWorkGroup.WorkGroupConfigurationProperty = {
  enforceWorkGroupConfiguration: true
};

// This should not match the pattern as it includes enforceWorkGroupConfiguration set to true
const workgroupWithEnforcement = new athena.CfnWorkGroup(this, 'workgroupWithEnforcement', {
  // other configuration details
  enforceWorkGroupConfiguration: true
});


// This should not match the pattern as it includes enforceWorkGroupConfiguration set to true
const workgroupWithEnforcement2 = new athena.CfnWorkGroup(this, 'workgroupWithEnforcement', workgroupConfig);
