resource "aws_mq_broker" "unknown" {
  broker_name = "example"

  engine_type         = "ActiveMQ"
  engine_version      = var.engine_version
  host_instance_type  = "mq.t2.micro"
  publicly_accessible = true
  deployment_mode     = "SINGLE_INSTANCE"
  # auto_minor_version_upgrade = true
  user {
    username = "ExampleUser"
    password = "MindTheGapps"  # checkov:skip=CKV_SECRET_6 test secret
  }
}


resource "aws_mq_broker" "fail" {
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
  engine_version      = "5.17.6"
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
  engine_version      = "3.11.20"
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

resource "aws_mq_configuration" "fail" {
  description    = "Example Configuration"
  name           = "example"
  engine_type    = "ActiveMQ"
  engine_version = "5.15.0"

  data = <<DATA
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<broker xmlns="http://activemq.apache.org/schema/core">
  <plugins>
    <forcePersistencyModeBrokerPlugin persistenceFlag="true"/>
    <statisticsBrokerPlugin/>
    <timeStampingBrokerPlugin ttlCeiling="86400000" zeroExpirationOverride="86400000"/>
  </plugins>
</broker>
DATA
}

resource "aws_mq_configuration" "pass" {
  description    = "Example Configuration"
  name           = "example"
  engine_type    = "ActiveMQ"
  engine_version = "5.17.6"

  data = <<DATA
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<broker xmlns="http://activemq.apache.org/schema/core">
  <plugins>
    <forcePersistencyModeBrokerPlugin persistenceFlag="true"/>
    <statisticsBrokerPlugin/>
    <timeStampingBrokerPlugin ttlCeiling="86400000" zeroExpirationOverride="86400000"/>
  </plugins>
</broker>
DATA
}


