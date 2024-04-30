import { aws_neptune as neptune } from 'aws-cdk-lib';

const cfnDBCluster1 = new neptune.CfnDBCluster(this, 'MyCfnDBCluster', /* all optional props */ {
  associatedRoles: [{
    roleArn: 'roleArn',

    // the properties below are optional
    featureName: 'featureName',
  }],
  availabilityZones: ['availabilityZones'],
  backupRetentionPeriod: 123,
  copyTagsToSnapshot: false,
  dbClusterIdentifier: 'dbClusterIdentifier',
  dbClusterParameterGroupName: 'dbClusterParameterGroupName',
  dbInstanceParameterGroupName: 'dbInstanceParameterGroupName',
  dbPort: 123,
  dbSubnetGroupName: 'dbSubnetGroupName',
  deletionProtection: false,
  enableCloudwatchLogsExports: ['enableCloudwatchLogsExports'],
  engineVersion: 'engineVersion',
  iamAuthEnabled: false,
  kmsKeyId: 'kmsKeyId',
  preferredBackupWindow: 'preferredBackupWindow',
  preferredMaintenanceWindow: 'preferredMaintenanceWindow',
  restoreToTime: 'restoreToTime',
  restoreType: 'restoreType',
  serverlessScalingConfiguration: {
    maxCapacity: 123,
    minCapacity: 123,
  },
  snapshotIdentifier: 'snapshotIdentifier',
  sourceDbClusterIdentifier: 'sourceDbClusterIdentifier',
  storageEncrypted: false,
  tags: [{
    key: 'key',
    value: 'value',
  }],
  useLatestRestorableTime: false,
  vpcSecurityGroupIds: ['vpcSecurityGroupIds'],
});

const cfnDBCluster2 = new neptune.CfnDBCluster(this, 'MyCfnDBCluster', /* all optional props */ {
  storageEncrypted: false,
});