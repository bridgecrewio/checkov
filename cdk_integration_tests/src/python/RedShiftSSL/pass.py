from aws_cdk import core
from aws_cdk import aws_redshift as redshift

class MyRedshiftClusterParameterGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Redshift Cluster Parameter Group with require_ssl parameter
        redshift.CfnClusterParameterGroup(
            self, 'MyRedshiftClusterParameterGroup',
            description='My Redshift Parameter Group',
            parameter_group_family='redshift-1.0',
            parameters=[
                redshift.CfnClusterParameterGroup.ParameterProperty(
                    parameter_name='require_ssl',
                    parameter_value='true'
                )
                # Add other parameters if needed
            ]
        )

app = core.App()
MyRedshiftClusterParameterGroupStack(app, "MyRedshiftClusterParameterGroupStack")
app.synth()


class MyRedshiftClusterParameterGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Redshift Cluster Parameter Group with require_ssl parameter
        redshift.CfnClusterParameterGroup(
            self, 'MyRedshiftClusterParameterGroup',
            description='My Redshift Parameter Group',
            parameter_group_family='redshift-1.0',
            parameters=[
                redshift.CfnClusterParameterGroup.ParameterProperty(
                    parameter_value='true',
                    parameter_name='require_ssl'
                )
                # Add other parameters if needed
            ]
        )

app = core.App()
MyRedshiftClusterParameterGroupStack(app, "MyRedshiftClusterParameterGroupStack")
app.synth()


class MyRedshiftClusterParameterGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Redshift Cluster Parameter Group with require_ssl parameter
        redshift.CfnClusterParameterGroup(
            self, 'MyRedshiftClusterParameterGroup',
            description='My Redshift Parameter Group',
            parameter_group_family='redshift-1.0',
            parameters=[
                {'parameterName': 'require_ssl','parameterValue': 'true'}
                # Add other parameters if needed
            ]
        )

app = core.App()
MyRedshiftClusterParameterGroupStack(app, "MyRedshiftClusterParameterGroupStack")
app.synth()


class MyRedshiftClusterParameterGroupStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Redshift Cluster Parameter Group with require_ssl parameter
        redshift.CfnClusterParameterGroup(
            self, 'MyRedshiftClusterParameterGroup',
            description='My Redshift Parameter Group',
            parameter_group_family='redshift-1.0',
            parameters=[
                {'parameterValue': 'true','parameterName': 'require_ssl'}
                # Add other parameters if needed
            ]
        )

app = core.App()
MyRedshiftClusterParameterGroupStack(app, "MyRedshiftClusterParameterGroupStack")
app.synth()


