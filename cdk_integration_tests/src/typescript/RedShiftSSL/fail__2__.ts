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
                    parameterValue: 'false',
                },
                // Add other parameters if needed
            ],
        });
    }
}

const app = new cdk.App();
new MyRedshiftClusterParameterGroupStack(app, 'MyRedshiftClusterParameterGroupStack');
app.synth();

class MyRedshiftClusterParameterGroupStack2 extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Define Redshift Cluster Parameter Group with abc parameter
        new redshift.CfnClusterParameterGroup(this, 'MyRedshiftClusterParameterGroup2', {
            description: 'My Redshift Parameter Group 2',
            parameterGroupFamily: 'redshift-1.0',
        });
    }
}

new MyRedshiftClusterParameterGroupStack2(app, 'MyRedshiftClusterParameterGroupStack2');
app.synth();
