import * as cdk from 'aws-cdk-lib';
import {aws_eks as eks} from 'aws-cdk-lib';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const cfnCluster = new eks.CfnCluster(this, 'MyCfnCluster', {
            resourcesVpcConfig: {
                subnetIds: ['subnetIds']
            },
            roleArn: 'roleArn',
            encryptionConfig: [{
                resources: ['secrets']
            }],
            name: 'name',
            version: 'version'
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
