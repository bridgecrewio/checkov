// SOURCE
import { Cluster } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to missing logging enabled
let bucketName;
let stack;
new Cluster(stack, 'MyRedshiftCluster', {
    masterUser: {
        masterUsername: 'admin',
        masterPassword: 'password',
    },
    logging_properties: Cluster.LoggingPropertiesProperty = {bucketName: 'name'}
    // logging enabled missing
});