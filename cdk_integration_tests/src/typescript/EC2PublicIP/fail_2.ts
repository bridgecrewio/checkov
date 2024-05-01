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

        const sg1 = new ec2.SecurityGroup(this, 'sg1', {
            vpc: vpc,
        });

        const launchTemplate = new ec2.LaunchTemplate(this, 'LaunchTemplate', {
            machineImage: ec2.MachineImage.latestAmazonLinux2023(),
            securityGroup: sg1,
            associatePublicIpAddress: true
        });

    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
