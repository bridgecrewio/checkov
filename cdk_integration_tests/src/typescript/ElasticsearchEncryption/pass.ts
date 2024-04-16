import * as cdk from 'aws-cdk-lib';
import * as elasticsearch from 'aws-cdk-lib/aws-elasticsearch';


const domain = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    encryptionAtRestOptions: {
        enabled: true, // Enable encryption at rest
        kmsKeyId: 'your-KMS-key-ID', // Specify your KMS key ID
    },
});

const domain3 = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
    encryptionAtRestOptions: {
        enabled: true, // Enable encryption at rest
    }
});

const encryptionAtRestOptionsProperty3: elasticsearch.CfnDomain.EncryptionAtRestOptionsProperty = {
    enabled: true,
};
