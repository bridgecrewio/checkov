resource "aws_emr_cluster" "cluster_ok" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  ec2_attributes {
    emr_managed_master_security_group = aws_security_group.block_access_ok.id
    emr_managed_slave_security_group  = aws_security_group.block_access_ok.id
    instance_profile                  = "connected_to_aws_iam_instance_profile"
  }
}

resource "aws_security_group" "block_access_ok" {
  name        = "block_access"
  description = "Block all traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.1/10"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.10/10"]
  }
}

resource "aws_emr_cluster" "cluster_not_connected" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  ec2_attributes {
    instance_profile                  = "connected_to_aws_iam_instance_profile"
  }
}


resource "aws_emr_cluster" "cluster_connected_to_wrong_group" {
  name          = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications  = ["Spark"]

  ec2_attributes {
    emr_managed_master_security_group = aws_security_group.block_access_not_ok.id
    emr_managed_slave_security_group  = aws_security_group.block_access_not_ok.id
    instance_profile                  = "connected_to_aws_iam_instance_profile"
  }
}

resource "aws_security_group" "block_access_not_ok" {
  name        = "block_access"
  description = "Block all traffic"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
