import {aws_autoscaling as autoscaling} from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1: autoscaling.CfnLaunchConfigurationProps = {
    imageId: 'imageId',
    instanceType: 'instanceType',

    // the properties below are optional
    associatePublicIpAddress: false,
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
    classicLinkVpcId: 'classicLinkVpcId',
    classicLinkVpcSecurityGroups: ['classicLinkVpcSecurityGroups'],
    ebsOptimized: false,
    iamInstanceProfile: 'iamInstanceProfile',
    instanceId: 'instanceId',
    instanceMonitoring: false,
    kernelId: 'kernelId',
    keyName: 'keyName',
    launchConfigurationName: 'launchConfigurationName',
    metadataOptions: {
        httpEndpoint: 'httpEndpoint',
        httpPutResponseHopLimit: 123,
        httpTokens: 'httpTokens',
    },
    placementTenancy: 'placementTenancy',
    ramDiskId: 'ramDiskId',
    securityGroups: ['securityGroups'],
    spotPrice: 'spotPrice',
    userData: 'userData',
};
