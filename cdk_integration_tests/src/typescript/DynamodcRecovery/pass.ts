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
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true, // Enable point-in-time recovery for the table
      },
    });
  }
}

// Example usage
const app = new cdk.App();
new DynamoDBStack(app, 'DynamoDBStack');
app.synth();


export class DynamoDBStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the DynamoDB table with point-in-time recovery enabled
    const table = new dynamodb.Table(this, 'MyTable', {
      tableName: 'MyTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      readCapacity: 5,
      writeCapacity: 5,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Optional: specify removal policy
      timeToLiveAttribute: 'ttlAttribute', // Enable point-in-time recovery
      pointInTimeRecovery: true, // Enable point-in-time recovery
    });
  }
}

// Example usage
const app = new cdk.App();
new DynamoDBStack(app, 'DynamoDBStack');
app.synth();
