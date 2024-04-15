import * as cdk from 'aws-cdk-lib';
import * as dms from 'aws-cdk-lib/aws-dms';

export class DMSStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a DMS replication instance
    const replicationInstance = new dms.CfnReplicationInstance(this, 'MyCfnReplicationInstance', {
      replicationInstanceClass: 'replicationInstanceClass',

      // Optional properties
      allocatedStorage: 123,
      allowMajorVersionUpgrade: false,
      autoMinorVersionUpgrade: false,
      availabilityZone: 'availabilityZone',
      engineVersion: 'engineVersion',
      kmsKeyId: 'kmsKeyId',
      multiAz: false,
      preferredMaintenanceWindow: 'preferredMaintenanceWindow',
      publiclyAccessible: false, // Set publiclyAccessible to true
      replicationInstanceIdentifier: 'replicationInstanceIdentifier',
      replicationSubnetGroupIdentifier: 'replicationSubnetGroupIdentifier',
      resourceIdentifier: 'resourceIdentifier',
      tags: [{ key: 'key', value: 'value' }],
      vpcSecurityGroupIds: ['vpcSecurityGroupIds'],
    });
  }
}

// Example usage
const app = new cdk.App();
new DMSStack(app, 'DMSStack');
app.synth();
