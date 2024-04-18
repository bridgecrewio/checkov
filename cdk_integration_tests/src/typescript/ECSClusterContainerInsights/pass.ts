import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const vpc = new ec2.Vpc(this, 'Vpc', {maxAzs: 1});
        const cluster = new ecs.Cluster(this, 'EcsCluster', {vpc, containerInsights: true});
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
