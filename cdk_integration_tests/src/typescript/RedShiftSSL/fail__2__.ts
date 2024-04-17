// FINDING
import { CfnClusterParameterGroup } from '@aws-cdk/aws-redshift';

// SINK
// SINK: Vulnerability found due to Redshift not using SSL
new CfnClusterParameterGroup(stack, 'MyClusterParameterGroup', {
    description: 'Parameter group for my Redshift cluster',
    family: 'redshift-1.0',
    parameters: {
        require_ssl: 'false', // This should be 'true' to enforce SSL
    },
});
new CfnClusterParameterGroup(stack, 'MyClusterParameterGroup', {
    description: 'Parameter group for my Redshift cluster',
    family: 'redshift-1.0',
    parameters: {
        random_param: 100
    },
});