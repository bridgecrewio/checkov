import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_elasticloadbalancingv2 as elbv2 } from 'aws-cdk-lib';

class ALBDropHttpHeadersStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        new elbv2.CfnLoadBalancer(this, {protocol: 'HTTPS'})
        new elbv2.CfnLoadBalancer(this, {protocol: 'TLS'})
        new elbv2.CfnLoadBalancer(this, {protocol: 'TCP'})
        new elbv2.CfnLoadBalancer(this, {protocol: 'UDP'})
        new elbv2.CfnLoadBalancer(this, {protocol: 'TCP_UDP'})
        new elbv2.CfnLoadBalancer(this, {defaultActions: [{type: 'redirect', redirectConfig:{protocol: 'HTTPS'}}]})
    }
}

const app = new App();
new ALBDropHttpHeadersStack(app, 'ALBDropHttpHeadersStack');
