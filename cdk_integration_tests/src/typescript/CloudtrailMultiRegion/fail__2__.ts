import * as cdk from 'aws-cdk-lib';
import * as cloudtrail from 'aws-cdk-lib/aws-cloudtrail';
import * as kms from 'aws-cdk-lib/aws-kms';

export class CloudTrailStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a KMS key for CloudTrail encryption
    const kmsKey = new kms.Key(this, 'CloudTrailKmsKey');

    // Create a CloudTrail trail using CfnTrail
    const trail = new cloudtrail.CfnTrail(this, 'MyCfnTrail', {
      isMultiRegionTrail: false,
      enableLogFileValidation: true,
      includeGlobalServiceEvents: true,
      kmsKeyId: kmsKey.keyId,
      trailName: 'MyCloudTrail',
    });
  }
}


export class CloudTrailStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a KMS key for CloudTrail encryption
    const kmsKey = new kms.Key(this, 'CloudTrailKmsKey');

    // Create a CloudTrail trail using Trail construct
    const trail = new cloudtrail.Trail(this, 'MyTrail', {
      enableFileValidation: true,
      includeGlobalServiceEvents: true,
      encryptionKey: kmsKey,
      trailName: 'MyCloudTrail',
    });
  }
}
