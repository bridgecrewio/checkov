import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class DynamoDBStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the DynamoDB table
    const table = new dynamodb.CfnTable(this, 'MyTable', {
      tableName: 'MyTable',
      attributeDefinitions: [{ attributeName: 'id', attributeType: 'S' }],
      keySchema: [{ attributeName: 'id', keyType: 'HASH' }],
      provisionedThroughput: {
        readCapacityUnits: 5,
        writeCapacityUnits: 5,
      },
    });

    // Define the DynamoDB global table
    const globalTable = new dynamodb.CfnGlobalTable(this, 'MyGlobalTable', {
      globalTableName: 'MyGlobalTable',
      replicationGroup: [{
        region: 'us-east-1', // Replace with your preferred region
      }],
      sourceTableName: table.ref,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true, // Enable point-in-time recovery for the global table
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new DynamoDBStack(app, 'DynamoDBStack');
app.synth();
