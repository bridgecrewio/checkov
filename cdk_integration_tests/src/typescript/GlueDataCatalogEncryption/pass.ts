import { aws_glue as glue } from 'aws-cdk-lib';

const cfnDataCatalogEncryptionSettings = new glue.CfnDataCatalogEncryptionSettings(this, 'MyCfnDataCatalogEncryptionSettings', {
  catalogId: 'catalogId',
  dataCatalogEncryptionSettings: {
    connectionPasswordEncryption: {
      kmsKeyId: 'kmsKeyId',
      returnConnectionPasswordEncrypted: true,
    },
    encryptionAtRest: {
      catalogEncryptionMode: "SSE-KMS",
      catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
      sseAwsKmsKeyId: 'sseAwsKmsKeyId',
    },
  },
});

const cfnDataCatalogEncryptionSettingsProps: glue.CfnDataCatalogEncryptionSettingsProps = {
  catalogId: 'catalogId',
  dataCatalogEncryptionSettings: {
    connectionPasswordEncryption: {
      kmsKeyId: 'kmsKeyId',
      returnConnectionPasswordEncrypted: true,
    },
    encryptionAtRest: {
      catalogEncryptionMode : "SSE-KMS",
      catalogEncryptionServiceRole: 'catalogEncryptionServiceRole',
      sseAwsKmsKeyId: 'sseAwsKmsKeyId',
    },
  },
};