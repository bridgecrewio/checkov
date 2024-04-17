import { App, Stack } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

class MyVpcEndpointServiceStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define VPC Endpoint Service with acceptance not required
    new ec2.CfnVPCEndpointService(this, 'MyVPCEndpointService', {
      acceptanceRequired: true,
      // Other properties for your VPC Endpoint Service
    });
  }
}

const app = new App();
new MyVpcEndpointServiceStack(app, "MyVpcEndpointServiceStack");
app.synth();
