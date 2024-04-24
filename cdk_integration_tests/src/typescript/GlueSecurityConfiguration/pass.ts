import { aws_glue as glue } from 'aws-cdk-lib';

const cfnSecurityConfiguration = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{
      kmsKeyArn: 'kmsKeyArn',
      s3EncryptionMode: 'SSE-KMS',
    }],
  },
  name: 'name',
});

const cfnSecurityConfiguration2 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{
      kmsKeyArn: 'kmsKeyArn',
      s3EncryptionMode: 'SSE-S3',
    }],
  },
  name: 'name',
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
