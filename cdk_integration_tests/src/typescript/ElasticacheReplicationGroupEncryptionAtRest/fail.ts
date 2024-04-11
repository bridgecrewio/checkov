import * as cdk from 'aws-cdk-lib';
import {aws_elasticache as elasticache} from 'aws-cdk-lib';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const cfnReplicationGroup = new elasticache.CfnReplicationGroup(this, 'MyCfnReplicationGroup', {
            replicationGroupDescription: 'replicationGroupDescription',
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
