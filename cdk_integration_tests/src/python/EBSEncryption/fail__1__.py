from aws_cdk import core
from aws_cdk import aws_ec2 as ec2

class MyVolumeStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an EBS volume without encryption
        ebs_volume = ec2.Volume(
            self,
            "MyEBSVolume",
            availability_zone="us-east-1a",  # Replace with your desired availability zone
            size=100,  # Set the size of the volume as needed
            encrypted=False,  # Disable encryption (default is False)
            volume_type=ec2.EbsDeviceVolumeType.GP2,  # Specify the volume type
        )
