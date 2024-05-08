import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class AmazonMQBrokerPublicAccessStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);
        new elbv2.CfnBroker(this, {publiclyAccessible: true})
    }
}

const app = new App();
new AmazonMQBrokerPublicAccessStack(app, 'AmazonMQBrokerPublicAccessStack');
