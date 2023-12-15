from aws_cdk import core
from aws_cdk import aws_elasticsearch as elasticsearch

class MyElasticsearchDomainStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Elasticsearch Domain with Node-to-Node Encryption Enabled
        elasticsearch.CfnDomain(
            self, 'MyElasticsearchDomain',
            domain_name='my-elasticsearch-domain',
            elasticsearch_version='7.10',  # Replace with your desired Elasticsearch version
            node_to_node_encryption_options={
                'enabled': False
            }
            # Other properties for your Elasticsearch Domain
        )

app = core.App()
MyElasticsearchDomainStack(app, "MyElasticsearchDomainStack")
app.synth()
