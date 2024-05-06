import * as cdk from 'aws-cdk-lib';
import * as cloudtrail from 'aws-cdk-lib/aws-cloudtrail';
import * as kms from 'aws-cdk-lib/aws-kms';

export class CloudTrailStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a KMS key for CloudTrail encryption
    const kmsKey = new kms.Key(this, 'CloudTrailKmsKey');

    // Create a CloudTrail trail with the specified KMS key ID
    const trail = new cloudtrail.CfnTrail(this, 'MyTrail', {
      enableLogFileValidation: true,
      includeGlobalServiceEvents: true,
      isMultiRegionTrail: true,
      kmsKeyId: kmsKey.keyId, // Use the KMS key ID
      trailName: 'MyCloudTrail',
    });
  }
}

// Example usage
const app = new cdk.App();
new CloudTrailStack(app, 'CloudTrailStack');

export class CloudTrailStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    // Create a CloudTrail trail with the specified KMS key ID
    const trail = new cloudtrail.CfnTrail(this, 'MyTrail', {
      enableLogFileValidation: true,
      includeGlobalServiceEvents: true,
      isMultiRegionTrail: true,
      kmsKeyId: new kms.Key(this, 'CloudTrailKmsKey').keyId,
      trailName: 'MyCloudTrail',
    });
  }
}

// Example usage
const app = new cdk.App();
new CloudTrailStack(app, 'CloudTrailStack');
