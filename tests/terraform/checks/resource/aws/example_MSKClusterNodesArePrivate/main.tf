resource "aws_msk_cluster" "pass" {
  cluster_name           = "pike"
  kafka_version          = "3.2.0"
  number_of_broker_nodes = 2
  broker_node_group_info {
    storage_info {
      ebs_storage_info {
        volume_size = 1100
      }
    }
    client_subnets = [
      "subnet-0562ef1d304b968f4",
    "subnet-08895dbf9e060579b"]
    instance_type   = "kafka.t3.small"
    security_groups = ["sg-002ed1a53dc5fe0ad"]
    connectivity_info {
      public_access {
        type = "DISABLED"
      }
    }
  }
  client_authentication {
    sasl {
      scram = true
    }
  }
  configuration_info {
    arn      = ""
    revision = 0
  }
  encryption_info {
    encryption_at_rest_kms_key_arn = "arn:aws:kms:eu-west-2:680235478471:key/fd160011-126e-4bec-b370-c8765b5c6a37"
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = false
      }

      node_exporter {
        enabled_in_broker = false
      }
    }

  }
  tags = {
    pike = "permissions"
  }
}

resource "aws_msk_cluster" "pass2" {
  cluster_name           = "pike"
  kafka_version          = "3.2.0"
  number_of_broker_nodes = 2
  broker_node_group_info {
    storage_info {
      ebs_storage_info {
        volume_size = 1100
      }
    }
    client_subnets = [
      "subnet-0562ef1d304b968f4",
    "subnet-08895dbf9e060579b"]
    instance_type   = "kafka.t3.small"
    security_groups = ["sg-002ed1a53dc5fe0ad"]
  }
  client_authentication {
    sasl {
      scram = true
    }
  }
  configuration_info {
    arn      = ""
    revision = 0
  }
  encryption_info {
    encryption_at_rest_kms_key_arn = "arn:aws:kms:eu-west-2:680235478471:key/fd160011-126e-4bec-b370-c8765b5c6a37"
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = false
      }

      node_exporter {
        enabled_in_broker = false
      }
    }

  }
  tags = {
    pike = "permissions"
  }
}

resource "aws_msk_cluster" "fail" {
  cluster_name           = "pike"
  kafka_version          = "3.2.0"
  number_of_broker_nodes = 2
  broker_node_group_info {
    storage_info {
      ebs_storage_info {
        volume_size = 1100
      }
    }
    client_subnets = [
      "subnet-0562ef1d304b968f4",
      "subnet-08895dbf9e060579b"]
    instance_type   = "kafka.t3.small"
    security_groups = ["sg-002ed1a53dc5fe0ad"]
    connectivity_info {
      public_access {
        type = "SERVICE_PROVIDED_EIPS"
      }
    }
  }
  client_authentication {
    sasl {
      scram = true
    }
  }
  configuration_info {
    arn      = ""
    revision = 0
  }
  encryption_info {
    encryption_at_rest_kms_key_arn = "arn:aws:kms:eu-west-2:680235478471:key/fd160011-126e-4bec-b370-c8765b5c6a37"
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = false
      }

      node_exporter {
        enabled_in_broker = false
      }
    }

  }
  tags = {
    pike = "permissions"
  }
}
