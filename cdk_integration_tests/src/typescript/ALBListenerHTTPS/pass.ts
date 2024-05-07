import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class ALBListenerHTTPSStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new elbv2.CfnListener(this, {protocol: 'HTTPS'})
        new elbv2.CfnListener(this, {protocol: 'TLS'})
        new elbv2.CfnListener(this, {protocol: 'TCP'})
        new elbv2.CfnListener(this, {protocol: 'UDP'})
        new elbv2.CfnListener(this, {protocol: 'TCP_UDP'})
        new elbv2.CfnListener(this, {defaultActions: [{type: 'redirect', redirectConfig:{protocol: 'HTTPS'}}]})
    }
}

const app = new App();
new ALBListenerHTTPSStack(app, 'ALBListenerHTTPSStack');
