import { aws_glue as glue } from 'aws-cdk-lib';

const cfnDataCatalogEncryptionSettings = new glue.CfnDataCatalogEncryptionSettings(this, 'MyCfnDataCatalogEncryptionSettings', {
  catalogId: 'catalogId',
  dataCatalogEncryptionSettings: {
    connectionPasswordEncryption: {
      kmsKeyId: 'kmsKeyId',
      returnConnectionPasswordEncrypted: false,
    },
    encryptionAtRest: {
      catalogEncryptionMode: 'SSE-KMS',
      catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
      sseAwsKmsKeyId: 'sseAwsKmsKeyId',
    },
  },
});

const cfnDataCatalogEncryptionSettings2 = new glue.CfnDataCatalogEncryptionSettings(this, 'MyCfnDataCatalogEncryptionSettings', {
  catalogId: 'catalogId',
  dataCatalogEncryptionSettings: {
    connectionPasswordEncryption: {
      returnConnectionPasswordEncrypted: true,
    },
    encryptionAtRest: {
      catalogEncryptionMode: 'DISABLED',
      catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
      sseAwsKmsKeyId: 'sseAwsKmsKeyId',
    },
  },
});

