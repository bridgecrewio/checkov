resource "aws_networkfirewall_firewall" "fail" {
  name                = "example"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.example.arn
  vpc_id              = aws_vpc.example.id
  subnet_mapping {
    subnet_id = aws_subnet.example.id
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }
}

resource "aws_networkfirewall_firewall" "fail2" {
  name                = "example"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.example.arn
  vpc_id              = aws_vpc.example.id
  subnet_mapping {
    subnet_id = aws_subnet.example.id
  }

  encryption_configuration {
    type="AWS_OWNED_KMS_KEY"
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }
  delete_protection = false
}

resource "aws_networkfirewall_firewall" "pass" {
  name                = "example"
  firewall_policy_arn = aws_networkfirewall_firewall_policy.example.arn
  vpc_id              = aws_vpc.example.id
  subnet_mapping {
    subnet_id = aws_subnet.example.id
  }

  encryption_configuration {
    key_id=aws_kms_key.pike.id
    type="CUSTOMER_KMS"
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }

  delete_protection = true
}

resource "aws_networkfirewall_rule_group" "fail" {
  capacity = 100
  name     = "example"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      rules_source_list {
        generated_rules_type = "DENYLIST"
        target_types         = ["HTTP_HOST"]
        targets              = ["test.example.com"]
      }
    }
    reference_sets {
      ip_set_references {
        key = "example"
        ip_set_reference {
          reference_arn = aws_ec2_managed_prefix_list.this.arn
        }
      }
    }
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }
}

resource "aws_networkfirewall_rule_group" "pass" {
  capacity = 100
  name     = "example"
  type     = "STATEFUL"
  rule_group {
    rules_source {
      rules_source_list {
        generated_rules_type = "DENYLIST"
        target_types         = ["HTTP_HOST"]
        targets              = ["test.example.com"]
      }
    }
    reference_sets {
      ip_set_references {
        key = "example"
        ip_set_reference {
          reference_arn = aws_ec2_managed_prefix_list.this.arn
        }
      }
    }
  }

  encryption_configuration {
    key_id=aws_kms_key.pike.id
    type="CUSTOMER_KMS"
  }
  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }
}