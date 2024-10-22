
resource "aws_mq_broker" "pass" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.fail.id
    revision = aws_mq_configuration.fail.latest_revision
  }

  engine_type        = "ActiveMQ"
  engine_version     = "5.15.13"
  host_instance_type = "mq.t2.micro"
  security_groups    = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"  # checkov:skip=CKV_SECRET_6 test secret
  }

  encryption_options {
    use_aws_owned_key = false
    kms_key_id        = aws_kms_key.example.arn
  }
}


resource "aws_mq_broker" "fail" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.fail.id
    revision = aws_mq_configuration.fail.latest_revision
  }

  engine_type        = "ActiveMQ"
  engine_version     = "5.15.13"
  host_instance_type = "mq.t2.micro"
  security_groups    = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  encryption_options {
    use_aws_owned_key = true
  }
}

resource "aws_mq_broker" "fail2" {
  broker_name = "example"

  configuration {
    id       = aws_mq_configuration.fail.id
    revision = aws_mq_configuration.fail.latest_revision
  }

  engine_type        = "ActiveMQ"
  engine_version     = "5.15.13"
  host_instance_type = "mq.t2.micro"
  security_groups    = [aws_security_group.test.id]

  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }
}
