import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
            volumes:
            [
                {
                    name:"my-volume",
                    efsVolumeConfiguration:{
                        transitEncryption: "DISABLED"
                    }
                }
            ]
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
