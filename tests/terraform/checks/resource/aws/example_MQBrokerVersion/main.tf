
resource "aws_mq_broker" "failure" {
  broker_name = "example"

  engine_type         = "ActiveMQ"
  engine_version      = "5.15.0"
  host_instance_type  = "mq.t2.micro"
  publicly_accessible = true
  deployment_mode     = "SINGLE_INSTANCE"
  # auto_minor_version_upgrade = true
  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # publicly_accessible = true
}

resource "aws_mq_broker" "pass" {
  broker_name = "example"

  engine_type         = "ActiveMQ"
  engine_version      = "5.16.0"
  host_instance_type  = "mq.t2.micro"
  publicly_accessible = true
  deployment_mode     = "SINGLE_INSTANCE"
  # auto_minor_version_upgrade = true
  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # publicly_accessible = true
}

resource "aws_mq_broker" "pass2" {
  broker_name = "example"

  engine_type         = "RabbitMQ"
  engine_version      = "3.8.6"
  host_instance_type  = "mq.t2.micro"
  publicly_accessible = true
  deployment_mode     = "SINGLE_INSTANCE"
  # auto_minor_version_upgrade = true
  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # publicly_accessible = true
}

#no failing major versions yet
resource "aws_mq_broker" "fail2" {
  broker_name = "example"

  engine_type         = "RabbitMQ"
  engine_version      = "3.7.6"
  host_instance_type  = "mq.t2.micro"
  publicly_accessible = true
  deployment_mode     = "SINGLE_INSTANCE"
  # auto_minor_version_upgrade = true
  user {
    username = "ExampleUser"
    password = "MindTheGapps"
  }

  # publicly_accessible = true
}