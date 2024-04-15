import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export class EC2Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create an EC2 instance
    const instance = new ec2.Instance(this, 'MyInstance', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
      machineImage: ec2.MachineImage.latestAmazonLinux(),
      vpc: new ec2.Vpc(this, 'MyVpc'),
    });

    // Create an EBS volume with encryption enabled
    const volume = new ec2.Volume(this, 'MyVolume', {
      availabilityZone: instance.instanceAvailabilityZone,
      size: ec2.Size.gibibytes(10), // Specify the volume size
      encrypted: true, // Enable encryption for the volume
    });

    // Attach the volume to the instance
    instance.instance.addVolumeAttachment('MyVolumeAttachment', {
      volume,
      device: '/dev/sdf', // Specify the device name
    });
  }
}

// Example usage
const app = new cdk.App();
new EC2Stack(app, 'EC2Stack');
app.synth();



export class EC2Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create an EC2 instance
    const instance = new ec2.Instance(this, 'MyInstance', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
      machineImage: ec2.MachineImage.latestAmazonLinux(),
      vpc: new ec2.Vpc(this, 'MyVpc'),
    });

    // Create an EBS volume with encryption enabled
    const volume = new ec2.CfnVolume(this, 'MyVolume', {
      availabilityZone: instance.instanceAvailabilityZone,
      size: 10, // Specify the volume size in GiB
      encrypted: true, // Enable encryption for the volume
    });

    // Attach the volume to the instance
    new ec2.CfnVolumeAttachment(this, 'MyVolumeAttachment', {
      instanceId: instance.instanceId,
      volumeId: volume.ref,
      device: '/dev/sdf', // Specify the device name
    });
  }
}

// Example usage
const app = new cdk.App();
new EC2Stack(app, 'EC2Stack');
app.synth();
