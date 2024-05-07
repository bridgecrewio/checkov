import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const vpc = new ec2.Vpc(this, 'VPC')
        const loggingBucket = new s3.Bucket(this, 'loggingBucket', {
            encryption: s3.BucketEncryption.S3_MANAGED,
        });
        const lb = new elbv2.ApplicationLoadBalancer(this, 'LB', {
            vpc
        });

        lb.logAccessLogs(loggingBucket);
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
