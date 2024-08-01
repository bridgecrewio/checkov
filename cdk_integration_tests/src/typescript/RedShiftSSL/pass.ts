import * as cdk from 'aws-cdk-lib';
import * as redshift from 'aws-cdk-lib/aws-redshift';

class MyRedshiftClusterParameterGroupStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Define Redshift Cluster Parameter Group with require_ssl parameter
        new redshift.CfnClusterParameterGroup(this, 'MyRedshiftClusterParameterGroup', {
            description: 'My Redshift Parameter Group',
            parameterGroupFamily: 'redshift-1.0',
            parameters: [
                {
                    parameterName: 'require_ssl',
                    parameterValue: 'true',
                },
                // Add other parameters if needed
            ],
        });
    }
}

const app = new cdk.App();
new MyRedshiftClusterParameterGroupStack(app, 'MyRedshiftClusterParameterGroupStack');
app.synth();
