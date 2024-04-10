import * as cdk from 'aws-cdk-lib';
import * as elasticsearch from 'aws-cdk-lib/aws-elasticsearch';


const domain = new elasticsearch.CfnDomain(this, 'MyElasticsearchDomain', {
  encryptionAtRestOptions: {
    enabled: true, // Enable encryption at rest
    kmsKeyId: 'your-KMS-key-ID', // Specify your KMS key ID
  },
});
