from aws_cdk import core
from aws_cdk import aws_appsync as appsync

class AppSyncStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the GraphQL API using CfnGraphQLApi
        graphql_api = appsync.CfnGraphQLApi(
            self,
            "AppSyncGraphQLApi",
            name="MyAppSyncAPI",
            authentication_type="API_KEY",  # You can change the authentication type
            log_config=appsync.CfnGraphQLApi.LogConfigProperty(
                cloud_watch_logs_role_arn="cloudWatchLogsRoleArn",
                exclude_verbose_content=False,
                field_log_level=appsync.FieldLogLevel.ALL
            ),
        )


app = core.App()
AppSyncStack(app, "AppSyncStack")
app.synth()
