import * as cdk from 'aws-cdk-lib';
import * as docdb from 'aws-cdk-lib/aws-docdb';
import * as kms from 'aws-cdk-lib/aws-kms';

export class DocDBStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a KMS key for DocumentDB storage encryption
    const kmsKey = new kms.Key(this, 'DocDBEncryptionKey');

    // Create an Amazon DocumentDB cluster
    const cluster = new docdb.CfnDBCluster(this, 'MyCluster', {
      dbClusterIdentifier: 'MyCluster',
      masterUsername: 'admin',
      masterUserPassword: 'mysecretpassword',
      dbSubnetGroupName: 'MySubnetGroup',
      engineVersion: '4.0.0',
      storageEncrypted: false, // Enable storage encryption
      kmsKeyId: kmsKey.keyArn,
      vpcSecurityGroupIds: ['sg-12345678'],
    });
  }
}

// Example usage
const app = new cdk.App();
new DocDBStack(app, 'DocDBStack');
app.synth();


export class DocDBStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a KMS key for DocumentDB storage encryption
    const kmsKey = new kms.Key(this, 'DocDBEncryptionKey');

    // Create an Amazon DocumentDB cluster
    const cluster = new docdb.CfnDBCluster(this, 'MyCluster', {
      dbClusterIdentifier: 'MyCluster',
      masterUsername: 'admin',
      masterUserPassword: 'mysecretpassword',
      dbSubnetGroupName: 'MySubnetGroup',
      engineVersion: '4.0.0',
      kmsKeyId: kmsKey.keyArn,
      vpcSecurityGroupIds: ['sg-12345678'],
    });
  }
}

// Example usage
const app = new cdk.App();
new DocDBStack(app, 'DocDBStack');
app.synth();