provider "aws" {
    region="us-east-1"
}

resource "aws_emr_cluster" "passing_cluster" {
  name          = "good"
  release_label = "release"
  applications  = ["Spark"]
  security_configuration = aws_emr_security_configuration.good_config.name
  ec2_attributes {
    subnet_id = aws_subnet.main.id
    instance_profile = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_count = 1
    instance_type  = "m5.xlarge"
  }
  service_role = aws_iam_role.iam_emr_service_role.arn
}


resource "aws_emr_security_configuration" "good_config" {
  name = "good"
# compliant case EncryptionConfiguration.EnableAtRestEncryption is true and LocalDiskEncryptionConfiguration exists
# Compliant EnableInTransitEncryption is true
# Compliant securityConfiguration exists and attaced with cluster
  configuration = <<EOF
{
  "EncryptionConfiguration": {
      "AtRestEncryptionConfiguration": {
            "LocalDiskEncryptionConfiguration": {
                "EncryptionKeyProviderType": "AwsKms",
                "AwsKmsKey": "${aws_kms_key.test.arn}"
            }
        },
        "EnableInTransitEncryption": true,
        "EnableAtRestEncryption": true
    }
}
EOF
}



resource "aws_emr_cluster" "also_passing_cluster" {
  name          = "good"
  release_label = "release"
  applications  = ["Spark"]
  security_configuration = aws_emr_security_configuration.also_good_config.name
  ec2_attributes {
    subnet_id = aws_subnet.main.id
    instance_profile = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_count = 1
    instance_type  = "m5.xlarge"
  }
  service_role = aws_iam_role.iam_emr_service_role.arn
}


resource "aws_emr_security_configuration" "also_good_config" {
  name = "good"
  data_retention = "5"
# compliant case EncryptionConfiguration.EnableAtRestEncryption is true and LocalDiskEncryptionConfiguration exists
# Compliant EnableInTransitEncryption is true
# Compliant securityConfiguration exists and attaced with cluster
  configuration = <<EOF
{
  "EncryptionConfiguration": {
      "AtRestEncryptionConfiguration": {
            "LocalDiskEncryptionConfiguration": {
                "EncryptionKeyProviderType": "AwsKms",
                "AwsKmsKey": "${aws_kms_key.test.arn}"
            }
        },
        "EnableInTransitEncryption": "true",
        "EnableAtRestEncryption": "true"
    }
}
EOF
}

resource "aws_emr_cluster" "failing_cluster" {
  name          = "bad"
  release_label = "release"
  applications  = ["Spark"]
  security_configuration = aws_emr_security_configuration.bad_config.name
  ec2_attributes {
    subnet_id = aws_subnet.main.id
    instance_profile = aws_iam_instance_profile.emr_profile.arn
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_count = 1
    instance_type  = "m5.xlarge"
  }
  service_role = aws_iam_role.iam_emr_service_role.arn
}


resource "aws_emr_security_configuration" "bad_config" {
  name = "bad"
# compliant case EncryptionConfiguration.EnableAtRestEncryption is true and LocalDiskEncryptionConfiguration exists
# Compliant EnableInTransitEncryption is true
# Compliant securityConfiguration exists and attaced with cluster
  configuration = <<EOF
{
  "EncryptionConfiguration": {
      "AtRestEncryptionConfiguration": {
            "LocalDiskEncryptionConfiguration": {
                "EncryptionKeyProviderType": "AwsKms",
                "AwsKmsKey": "${aws_kms_key.test.arn}"
            }
        },
        "EnableInTransitEncryption": false,
        "EnableAtRestEncryption": true
    }
}
EOF
}

