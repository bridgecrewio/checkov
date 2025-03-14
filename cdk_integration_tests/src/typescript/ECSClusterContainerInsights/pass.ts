import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const vpc = new ec2.Vpc(this, 'Vpc', {maxAzs: 1});
        const cluster = new ecs.Cluster(this, 'EcsCluster', {vpc, containerInsights: true});
        const cluster2 = new ecs.Cluster(this, 'EcsCluster2', {vpc, containerInsightsV2: ecs.ContainerInsights.ENABLED});
        const cluster3 = new ecs.Cluster(this, 'EcsCluster6', {vpc, containerInsightsV2: ecs.ContainerInsights.ENHANCED});

        const cluster4 = new ecs.CfnCluster(this, 'EcsCluster4', {clusterSettings: [{name: 'containerInsights', value: 'enabled'}]});
        const cluster5 = new ecs.CfnCluster(this, 'EcsCluster5', {clusterSettings: [{value: 'enhanced', name: 'containerInsights'}]});
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
