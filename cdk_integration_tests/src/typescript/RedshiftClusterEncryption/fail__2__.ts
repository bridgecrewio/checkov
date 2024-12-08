import * as redshift from '@aws-cdk/aws-redshift-alpha';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Stack, App } from 'aws-cdk-lib';

const app = new App();
const stack = new Stack(app, 'RedshiftStack');

// Create a VPC
const vpc = new ec2.Vpc(stack, 'Vpc', {
    maxAzs: 2
});

// Create a KMS key for encryption
const kmsKey = new kms.Key(stack, 'KmsKey');

const cluster = new redshift.Cluster(stack, 'MyCluster', {
    masterUser: {
        masterUsername: 'admin',
    },
    vpc,
});

import * as redshift from 'aws-cdk-lib/aws_redshift';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Stack, App } from 'aws-cdk-lib';

const app = new App();
const stack = new Stack(app, 'RedshiftStack');

// Create a VPC
const vpc = new ec2.Vpc(stack, 'Vpc', {
    maxAzs: 2
});

// Create a KMS key for encryption
const kmsKey = new kms.Key(stack, 'KmsKey');

const cfnCluster = new redshift.CfnCluster(stack, 'MyCfnCluster', {
    clusterType: 'multi-node',
    dbName: 'mydatabase',
    masterUsername: 'admin',
    masterUserPassword: 'password',
    nodeType: 'ds2.xlarge',
    numberOfNodes: 3,
    kmsKeyId: kmsKey.keyArn, // Use the specific KMS key
    vpcSecurityGroupIds: [ /* security group IDs */ ],
    clusterSubnetGroupName: vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }).subnetIds[0],
});

