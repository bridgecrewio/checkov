import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const vpc = new ec2.Vpc(this, 'VPC', {
            cidr: '10.0.0.0/16',
            natGateways: 0,
            maxAzs: 2,
            subnetConfiguration: [
                {
                    name: 'public-subnet-1',
                    subnetType: ec2.SubnetType.PUBLIC,
                    cidrMask: 24,
                },
            ],
        });

        const instance = new ec2.Instance(this, 'Instance', {
            vpc,
            vpcSubnets: {subnetGroupName: 'public-subnet-1'},
            instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.NANO),
            machineImage: new ec2.AmazonLinuxImage({generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2}),
            detailedMonitoring: true,
            associatePublicIpAddress: true
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
