import * as cdk from 'aws-cdk-lib';
import * as docdb from 'aws-cdk-lib/aws-docdb';

export class DocDBStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the DocDB Cluster Parameter Group
    const dbParameterGroup = new docdb.CfnDBClusterParameterGroup(this, 'DocDBClusterParameterGroup', {
      description: 'Custom DocDB Cluster Parameter Group',
      family: 'docdb4.0',
      parameters: {
        tls: 'enabled',
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new DocDBStack(app, 'DocDBStack');
app.synth();