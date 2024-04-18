import { aws_elasticsearch as elasticsearch } from 'aws-cdk-lib';

const domain = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    nodeToNodeEncryptionOptions: {
        enabled: true, // Enable encryption at rest
    },
});

const domain3 = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    nodeToNodeEncryptionOptions: {
        enabled: true, // Enable encryption at rest
    }
});

const encryptionAtRestOptionsProperty3: elasticsearch.CfnDomain.NodeToNodeEncryptionOptionsProperty = {
    enabled: true,
};
