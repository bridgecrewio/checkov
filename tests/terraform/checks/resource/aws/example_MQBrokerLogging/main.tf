# pass

resource "aws_mq_broker" "enabled" {
  broker_name        = "example"
  engine_type        = "ActiveMQ"
  engine_version     = "5.16.3"
  host_instance_type = "mq.t3.micro"

  user {
    password = "admin123"
    username = "admin"
  }

  logs {
    general = true
  }
}

# fail

resource "aws_mq_broker" "default" {
  broker_name        = "example"
  engine_type        = "ActiveMQ"
  engine_version     = "5.16.3"
  host_instance_type = "mq.t3.micro"

  user {
    password = "admin123"
    username = "admin"
  }
}

resource "aws_mq_broker" "disabled" {
  broker_name        = "example"
  engine_type        = "ActiveMQ"
  engine_version     = "5.16.3"
  host_instance_type = "mq.t3.micro"

  user {
    password = "admin123"
    username = "admin"
  }

  logs {
    general = false
  }
}
