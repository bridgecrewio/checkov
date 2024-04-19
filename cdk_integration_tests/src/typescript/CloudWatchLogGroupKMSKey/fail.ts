import * as cdk from 'aws-cdk-lib';
import * as logs from 'aws-cdk-lib/aws-logs';

export class MyLogGroupStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new logs.LogGroup(this, 'MyLogGroup', {
      logGroupName: 'MyLogGroupName', // Name of the log group
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Setting removal policy
      retention: logs.RetentionDays.ONE_MONTH, // Set the retention policy as needed
    });

    // You can add other resources or configurations to the stack here
  }
}

// Example usage
const app = new cdk.App();
new MyLogGroupStack(app, 'MyLogGroupStack');
