
resource "aws_mq_broker" "fail" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.test.id
    revision = aws_mq_configuration.test.latest_revision
  }

  engine_type        = "ActiveMQ"
  engine_version     = "5.15.9"
  host_instance_type = "mq.t2.micro"
  security_groups    = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"  # checkov:skip=CKV_SECRET_6 test secret
  }

  # encryption_options {
  #   use_aws_owned_key=false
  #   kms_key_id=aws_kms_key.examplea.arn
  # }
}


resource "aws_mq_broker" "fail2" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.test.id
    revision = aws_mq_configuration.test.latest_revision
  }

  auto_minor_version_upgrade = false
  engine_type                = "ActiveMQ"
  engine_version             = "5.15.9"
  host_instance_type         = "mq.t2.micro"
  security_groups            = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # encryption_options {
  #   use_aws_owned_key=false
  #   kms_key_id=aws_kms_key.examplea.arn
  # }
}


resource "aws_mq_broker" "pass" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.test.id
    revision = aws_mq_configuration.test.latest_revision
  }

  auto_minor_version_upgrade = true
  engine_type                = "ActiveMQ"
  engine_version             = "5.15.9"
  host_instance_type         = "mq.t2.micro"
  security_groups            = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # encryption_options {
  #   use_aws_owned_key=false
  #   kms_key_id=aws_kms_key.examplea.arn
  # }
}

resource "aws_kms_key" "example" {

}
