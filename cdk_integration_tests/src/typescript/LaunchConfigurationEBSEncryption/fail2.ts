import {aws_autoscaling as autoscaling} from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new autoscaling.CfnLaunchConfiguration(this, 'MyCfnSecurityConfiguration', {
    imageId: 'imageId',
    instanceType: 'instanceType',
    blockDeviceMappings: [{
        deviceName: 'deviceName',

        // the properties below are optional
        ebs: {
            deleteOnTermination: false,
            encrypted: false,
            iops: 123,
            snapshotId: 'snapshotId',
            throughput: 123,
            volumeSize: 123,
            volumeType: 'volumeType',
        },
        noDevice: false,
        virtualName: 'virtualName',
    }],
});

const cfnSecurityConfiguration2 = new autoscaling.CfnLaunchConfiguration(this, 'MyCfnSecurityConfiguration', {
    blockDeviceMappings: [{
        ebs: {
            encrypted: false,
        },
    }],
});
