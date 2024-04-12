import * as cdk from 'aws-cdk-lib';
import * as es from 'aws-cdk-lib/aws-elasticsearch';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const domain = new es.Domain(this, 'Domain', {
            version: es.ElasticsearchVersion.V7_4,
            logging: {
                appLogEnabled: true
            }
        });
    }
}

const app = new cdk.App();
new exampleStack(app, 'example-stack');
app.synth();
