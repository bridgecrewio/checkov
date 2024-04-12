import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class APIGatewayV2AccessLoggingStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new elbv2.CfnApi(this, {})
    }
}

const app = new App();
new APIGatewayV2AccessLoggingStack(app, 'APIGatewayV2AccessLoggingStack');
