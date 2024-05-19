import { CfnClusterParameterGroup } from '@aws-cdk/aws-redshift';

new CfnClusterParameterGroup(stack, 'MyClusterParameterGroup', {
    description: 'Parameter group for my Redshift cluster',
    family: 'redshift-1.0',
    parameters: {
        require_ssl: 'true', // This should be 'true' to enforce SSL
    },
});