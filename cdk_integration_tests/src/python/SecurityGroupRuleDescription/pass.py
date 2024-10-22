from aws_cdk import core
from aws_cdk import aws_ec2 as ec2

class MySecurityGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define EC2 Security Group
        security_group = ec2.CfnSecurityGroup(
            self, 'MySecurityGroup',
            group_description='My security group',
            security_group_ingress=[
                {
                    'description': 'True',
                    'ipProtocol': 'tcp',
                    'fromPort': 80,
                    'toPort': 80,
                    'cidrIp': '0.0.0.0/0'
                }
            ],
            # Other properties for your Security Group
        )

app = core.App()
MySecurityGroupStack(app, "MySecurityGroupStack")
app.synth()



class MySecurityGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define EC2 Security Group
        security_group = ec2.CfnSecurityGroup(
            self, 'MySecurityGroup',
            group_description='My security group',
            security_group_egress=[
                {
                    'description': 'True',
                    'ipProtocol': 'tcp',
                    'fromPort': 80,
                    'toPort': 80,
                    'cidrIp': '0.0.0.0/0'
                }
            ],
            # Other properties for your Security Group
        )

app = core.App()
MySecurityGroupStack(app, "MySecurityGroupStack")
app.synth()


class MySecurityGroupIngressStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define EC2 Security Group Ingress
        security_group_ingress = ec2.CfnSecurityGroupIngress(
            self, 'MySecurityGroupIngress',
            group_id='your-security-group-id',  # Replace with your Security Group ID
            ip_protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_ip='0.0.0.0/0',
            description='abc'
            # Other properties for your Security Group Ingress
        )

app = core.App()
MySecurityGroupIngressStack(app, "MySecurityGroupIngressStack")
app.synth()

class MySecurityGroupEgressStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define EC2 Security Group Ingress
        security_group_ingress = ec2.CfnSecurityGroupEgress(
            self, 'MySecurityGroupIngress',
            group_id='your-security-group-id',  # Replace with your Security Group ID
            ip_protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_ip='0.0.0.0/0',
            description='abc'
            # Other properties for your Security Group Ingress
        )

app = core.App()
MySecurityGroupEgressStack(app, "MySecurityGroupEgressStack")
app.synth()
