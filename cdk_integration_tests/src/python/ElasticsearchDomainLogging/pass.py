from aws_cdk import core
from aws_cdk import aws_elasticsearch as elasticsearch
from aws_cdk import aws_opensearchservice as opensearchservice

class MyElasticsearchDomainStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elasticsearch Domain with LogPublishingOptions for different log types
        elasticsearch.CfnDomain(
            self, 'MyElasticsearchDomain',
            domain_name='my-elasticsearch-domain',
            elasticsearch_version='7.10',  # Replace with your desired Elasticsearch version
            node_to_node_encryption_options={
                'enabled': True
            },
            log_publishing_options={
                'logPublishingOptionsKey': elasticsearch.CfnDomain.LogPublishingOptionProperty(
                    cloud_watch_logs_log_group_arn='arn:aws:logs:REGION:ACCOUNT_ID:log-group:LOG_GROUP_NAME',
                    enabled=True
                )
            }
            # Other properties for your Elasticsearch Domain
        )

app = core.App()
MyElasticsearchDomainStack(app, "MyElasticsearchDomainStack")
app.synth()

class MyOpenSearchDomainStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define OpenSearch Service Domain with LogPublishingOptions for different log types
        opensearchservice.CfnDomain(
            self, 'MyOpenSearchDomain',
            domain_name='my-opensearch-domain',
            elasticsearch_version='7.10',  # Replace with your desired OpenSearch version
            node_to_node_encryption_options={
                'enabled': True
            },
            log_publishing_options={
                'logPublishingOptionsKey': opensearchservice.CfnDomain.LogPublishingOptionProperty(
                    cloud_watch_logs_log_group_arn='arn:aws:logs:REGION:ACCOUNT_ID:log-group:LOG_GROUP_NAME',
                    enabled=True
                )
            }
            # Other properties for your OpenSearch Service Domain
        )

app = core.App()
MyOpenSearchDomainStack(app, "MyOpenSearchDomainStack")
app.synth()
