import { App, Stack } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

class MySecurityGroupStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define EC2 Security Group with Ingress
    const securityGroup = new ec2.CfnSecurityGroup(this, 'MySecurityGroup', {
      groupDescription: 'My security group',
      securityGroupIngress: [
        {
          description: 'Allow HTTP inbound',
          ipProtocol: 'tcp',
          fromPort: 80,
          toPort: 80,
          cidrIp: '0.0.0.0/0',
        },
      ],
      // Other properties for your Security Group
    });
  }
}

class MySecurityGroupEgressStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define EC2 Security Group with Egress
    const securityGroupEgress = new ec2.CfnSecurityGroup(this, 'MySecurityGroup', {
      groupDescription: 'My security group',
      securityGroupEgress: [
        {
          description: 'Allow HTTP outbound',
          ipProtocol: 'tcp',
          fromPort: 80,
          toPort: 80,
          cidrIp: '0.0.0.0/0',
        },
      ],
      // Other properties for your Security Group
    });
  }
}

class MySecurityGroupIngressStack extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define EC2 Security Group Ingress
    new ec2.CfnSecurityGroupIngress(this, 'MySecurityGroupIngress', {
      groupId: 'your-security-group-id', // Replace with your Security Group ID
      ipProtocol: 'tcp',
      fromPort: 80,
      toPort: 80,
      cidrIp: '0.0.0.0/0',
      // Other properties for your Security Group Ingress
    });
  }
}

class MySecurityGroupEgressStack2 extends Stack {
  constructor(scope: Construct, id: string, props?: {}) {
    super(scope, id, props);

    // Define EC2 Security Group Egress
    new ec2.CfnSecurityGroupEgress(this, 'MySecurityGroupEgress', {
      groupId: 'your-security-group-id', // Replace with your Security Group ID
      ipProtocol: 'tcp',
      fromPort: 80,
      toPort: 80,
      cidrIp: '0.0.0.0/0',
      // Other properties for your Security Group Egress
    });
  }
}

const app = new App();
new MySecurityGroupStack(app, "MySecurityGroupStack");
new MySecurityGroupIngressStack(app, "MySecurityGroupIngressStack");
new MySecurityGroupEgressStack(app, "MySecurityGroupEgressStack");
app.synth();
