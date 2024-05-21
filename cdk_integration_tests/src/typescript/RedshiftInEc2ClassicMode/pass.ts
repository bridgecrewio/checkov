// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc: vpc,
    clusterSubnetGroupName: 'name'
});
