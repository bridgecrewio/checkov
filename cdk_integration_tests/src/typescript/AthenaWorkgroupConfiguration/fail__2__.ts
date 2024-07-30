// Import necessary AWS CDK packages
import * as athena from '@aws-cdk/aws-athena';

// Example of a Workgroup configuration
// FINDING
const workgroupConfig: athena.CfnWorkGroup.WorkGroupConfigurationProperty = {
  // Workgroup configuration details
};


const workgroupWithoutEnforcement2 = new athena.CfnWorkGroup(this, 'workgroupWithoutEnforcement', {
  // other configuration details
  workGroupConfiguration: workgroupConfig
});
