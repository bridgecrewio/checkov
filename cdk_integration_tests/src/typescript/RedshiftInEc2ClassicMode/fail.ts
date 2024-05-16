// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to Redshift cluster deployed outside of a VPC
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc: vpc
});
