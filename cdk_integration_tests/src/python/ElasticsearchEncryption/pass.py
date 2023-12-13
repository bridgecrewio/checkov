from aws_cdk import core
from aws_cdk import aws_elasticsearch as elasticsearch

class MyElasticsearchDomainStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elasticsearch Domain with Encryption At Rest Enabled
        elasticsearch.CfnDomain(
            self, 'MyElasticsearchDomain',
            domain_name='my-elasticsearch-domain',
            elasticsearch_version='7.10',  # Replace with your desired Elasticsearch version
            encryption_at_rest_options={
                'enabled': True
            }
            # Other properties for your Elasticsearch Domain
        )

app = core.App()
MyElasticsearchDomainStack(app, "MyElasticsearchDomainStack")
app.synth()
