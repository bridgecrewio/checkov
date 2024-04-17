import * as cdk from 'aws-cdk-lib';
import * as dax from 'aws-cdk-lib/aws-dax';

export class DAXClusterStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a DAX cluster
    const daxCluster = new dax.CfnCluster(this, 'MyDAXCluster', {
      clusterName: 'MyDAXCluster',
      description: 'My DAX Cluster',
      iamRoleArn: 'arn:aws:iam::123456789012:role/DAXServiceRole',
      nodeType: 'dax.r5.large',
      replicationFactor: 2,
      sseSpecification: {
        enabled: false, // Disable server-side encryption
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new DAXClusterStack(app, 'DAXClusterStack');
app.synth();

export class DAXClusterStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a DAX cluster
    const daxCluster = new dax.CfnCluster(this, 'MyDAXCluster', {
      clusterName: 'MyDAXCluster',
      description: 'My DAX Cluster',
      iamRoleArn: 'arn:aws:iam::123456789012:role/DAXServiceRole',
      nodeType: 'dax.r5.large',
      replicationFactor: 2,
    });
  }
}

// Example usage
const app = new cdk.App();
new DAXClusterStack(app, 'DAXClusterStack');
app.synth();