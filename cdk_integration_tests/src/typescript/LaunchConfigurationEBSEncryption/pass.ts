import { aws_autoscaling as autoscaling } from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new autoscaling.CfnLaunchConfiguration(this, 'MyCfnSecurityConfiguration', {
    imageId: 'imageId',
    instanceType: 'instanceType',
    blockDeviceMappings: [{
        deviceName: 'deviceName',

        // the properties below are optional
        ebs: {
            deleteOnTermination: false,
            encrypted: true,
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
    imageId: 'imageId',
    instanceType: 'instanceType',
    blockDeviceMappings: [{
        deviceName: 'deviceName',

        // the properties below are optional
        ebs: {
            deleteOnTermination: false,
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

const cfnSecurityConfiguration3 = new autoscaling.CfnLaunchConfiguration(this, 'MyCfnSecurityConfiguration', {
    imageId: 'imageId',
    instanceType: 'instanceType',
    blockDeviceMappings: [{
        deviceName: 'deviceName',
        noDevice: false,
        virtualName: 'virtualName',
    }],
});

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
            encrypted: true,
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

const cfnSecurityConfigurationProps2: autoscaling.CfnLaunchConfigurationProps = {
    imageId: 'imageId',
    instanceType: 'instanceType',

    // the properties below are optional
    associatePublicIpAddress: false,
    blockDeviceMappings: [{
        deviceName: 'deviceName',
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

const cfnSecurityConfigurationProps3: autoscaling.CfnLaunchConfigurationProps = {
    imageId: 'imageId',
    instanceType: 'instanceType',

    // the properties below are optional
    associatePublicIpAddress: false,
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

