import { aws_glue as glue } from 'aws-cdk-lib';

const cfnSecurityConfigurationProps1:  glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps2: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps3: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps4: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps5: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps6: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps7: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps8: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps9: glue.CfnSecurityConfigurationProps = {
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
};

const cfnSecurityConfigurationProps10: glue.CfnSecurityConfigurationProps =  {
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
};


