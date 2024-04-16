import { aws_elasticsearch as elasticsearch } from 'aws-cdk-lib';

const domain = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    nodeToNodeEncryptionOptions: {
        enabled: false, // Enable encryption at rest
        kmsKeyId: 'your-KMS-key-ID', // Specify your KMS key ID
    }
});

const domain2 = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    nodeToNodeEncryptionOptions: {
        enabled: false, // Enable encryption at rest
    }
});

