import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elb from 'aws-cdk-lib/aws-elasticloadbalancing';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const vpc = new ec2.Vpc(this, 'VPC')
        const lb = new elb.LoadBalancer(this, 'LB', {
            vpc
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
