// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to missing encryption at rest
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc, encrypted: true
});
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc
});
