import * as cdk from 'aws-cdk-lib';
import * as logs from 'aws-cdk-lib/aws-logs';

export class MyLogGroupStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Creating a CloudFormation LogGroup resource
    const logGroup = new logs.CfnLogGroup(this, 'MyLogGroup', {
      logGroupName: 'MyLogGroupName', // Name of the log group
      kmsKeyId: '1', // Specify the KMS key ID
    });

    // Optionally set removal policy
    logGroup.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
  }
}

// Example usage
const app = new cdk.App();
new MyLogGroupStack(app, 'MyLogGroupStack');
