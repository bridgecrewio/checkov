from aws_cdk import aws_apigateway as apigateway

cfn_stage = apigateway.CfnStage(self, "MyCfnStage",
    rest_api_id="restApiId",

    # the properties below are optional

    cache_cluster_enabled=False,
    cache_cluster_size="cacheClusterSize",
    canary_setting=apigateway.CfnStage.CanarySettingProperty(
        deployment_id="deploymentId",
        percent_traffic=123,
        stage_variable_overrides={
            "stage_variable_overrides_key": "stageVariableOverrides"
        },
        use_stage_cache=False
    ),
    client_certificate_id="clientCertificateId",
    deployment_id="deploymentId",
    description="description",
    documentation_version="documentationVersion",
    method_settings=[apigateway.CfnStage.MethodSettingProperty(
        cache_data_encrypted=False,
        cache_ttl_in_seconds=123,
        caching_enabled=False,
        data_trace_enabled=False,
        http_method="httpMethod",
        logging_level="loggingLevel",
        metrics_enabled=False,
        resource_path="resourcePath",
        throttling_burst_limit=123,
        throttling_rate_limit=123
    )],
    stage_name="stageName",
    tags=[CfnTag(
        key="key",
        value="value"
    )],
    tracing_enabled=False,
    variables={
        "variables_key": "variables"
    }
)

from aws_cdk import core
from aws_cdk import aws_serverless as serverless

class ServerlessApiWithAccessLogStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Serverless API
        serverless.Api(
            self, "MyApi",
            default_stage={
                "stage_name": "prod",
                "access_log_setting": serverless.AccessLogSetting(
                    format=serverless.AccessLogFormat.json_with_standard_fields()
                )
            }
        )

app = core.App()
ServerlessApiWithAccessLogStack(app, "ServerlessApiWithAccessLogStack")
app.synth()
