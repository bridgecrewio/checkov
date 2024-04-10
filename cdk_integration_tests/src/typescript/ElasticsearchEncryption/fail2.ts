import { aws_elasticsearch as elasticsearch } from 'aws-cdk-lib';

elasticsearch.CfnDomain.EncryptionAtRestOptionsProperty = { enabled: false, kmsKeyId: 'your-KMS-key-ID' };
