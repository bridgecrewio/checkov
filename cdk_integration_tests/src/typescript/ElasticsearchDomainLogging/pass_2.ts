import * as cdk from 'aws-cdk-lib';
import * as opensearch from 'aws-cdk-lib/aws-opensearchservice';
import {Construct} from 'constructs';

export class exampleStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const domain = new opensearch.Domain(this, 'Domain', {
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
