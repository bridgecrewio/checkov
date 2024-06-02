// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to publicly accessible cluster
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    vpc,
    publiclyAccessible: true, // publicly accessible cluster
});
