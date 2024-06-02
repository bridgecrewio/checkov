// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to missing logging enabled
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc
    // logging enabled missing
});
