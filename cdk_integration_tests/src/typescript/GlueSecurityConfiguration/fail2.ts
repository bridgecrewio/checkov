import { aws_glue as glue } from 'aws-cdk-lib';

const cfnSecurityConfiguration1 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [],
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
      jobBookmarksEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-S3" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration3 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-KMS" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration4 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "DISABLE" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration5 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "DISABLE" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration6 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-S3" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration7 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'DISABLE',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-KMS" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration8 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "DISABLE" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration9 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-KMS" }],
  },
  name: 'name',
});

const cfnSecurityConfiguration10 = new glue.CfnSecurityConfiguration(this, 'MyCfnSecurityConfiguration', {
  encryptionConfiguration: {
    cloudWatchEncryption: {
      cloudWatchEncryptionMode: 'SSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    jobBookmarksEncryption: {
      jobBookmarksEncryptionMode: 'CSE-KMS',
      kmsKeyArn: 'kmsKeyArn',
    },
    s3Encryptions: [{ s3EncryptionMode: "SSE-S3" }],
  },
  name: 'name',
});


