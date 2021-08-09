resource "aws_emr_security_configuration" "fail" {
  name = "fail"

  configuration = <<EOF
{
  "EncryptionConfiguration": {
    "EnableAtRestEncryption": true,
    "AtRestEncryptionConfiguration": {
      "S3EncryptionConfiguration": {
        "EncryptionMode": "SSE-S3"
      },
      "LocalDiskEncryptionConfiguration": {
        "EncryptionKeyProviderType": "AwsS3"
      }
    }
  }
}
EOF
}


resource "aws_emr_security_configuration" "pass" {
  name = "pass"

  configuration = <<EOF
{
  "EncryptionConfiguration": {
    "EnableAtRestEncryption": true,
    "AtRestEncryptionConfiguration": {
      "S3EncryptionConfiguration": {
        "EncryptionMode": "SSE-KMS",
        "AwsKmsKey": "${module.encryption_module.kms_key_alias}"
      },
      "LocalDiskEncryptionConfiguration": {
        "EncryptionKeyProviderType": "AwsKms",
        "AwsKmsKey": "${module.encryption_module.kms_key_alias}"
      }
    },
    "EnableInTransitEncryption": true
  }
}
EOF
}

