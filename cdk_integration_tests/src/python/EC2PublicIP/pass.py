from aws_cdk import core
from aws_cdk import aws_ec2 as ec2

class MyEC2InstanceStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define VPC for the EC2 Instance
        vpc = ec2.Vpc(
            self, 'MyVpc',
            max_azs=2  # Replace with the desired number of Availability Zones
        )

        # Define EC2 Instance with Network Interface having Public IP
        instance = ec2.CfnInstance(
            self, 'MyEC2Instance',
            image_id='ami-12345678',  # Replace with your desired AMI ID
            instance_type='t2.micro',  # Replace with your desired instance type
            network_interfaces=[{
                'deviceIndex': '0',
                'subnet_id': vpc.public_subnets[0].subnet_id,
                'associate_public_ip_address': False
            }]
            # Other properties for your EC2 Instance
        )

app = core.App()
MyEC2InstanceStack(app, "MyEC2InstanceStack")
app.synth()

class MyEC2LaunchTemplateStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Launch Template for the EC2 Instance
        launch_template = ec2.CfnLaunchTemplate(
            self, 'MyLaunchTemplate',
            launch_template_name='my-launch-template',
            launch_template_data={
                'network_interfaces': [{
                    'deviceIndex': '0',
                    'associate_public_ip_address': False
                }]
                # Other properties for your Launch Template Data
            }
        )

app = core.App()
MyEC2LaunchTemplateStack(app, "MyEC2LaunchTemplateStack")
app.synth()

