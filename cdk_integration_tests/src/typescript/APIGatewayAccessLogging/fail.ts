import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { apigateway as api } from 'aws-cdk-lib';

class APIGatewayAccessLoggingStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new api.CfnStage(this, {})
    }
}

const app = new App();
new APIGatewayAccessLoggingStack(app, 'APIGatewayAccessLoggingStack');
