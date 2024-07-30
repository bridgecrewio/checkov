import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as efs from 'aws-cdk-lib/aws-efs';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const fileSystem = new efs.FileSystem(this, 'MyEfsFileSystem', {
            vpc: new ec2.Vpc(this, 'VPC'),
            encrypted: true
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
