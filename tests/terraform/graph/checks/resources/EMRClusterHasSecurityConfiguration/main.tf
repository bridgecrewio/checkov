resource "aws_emr_cluster" "pass" {
  # ... other configuration ...

  # EMR version must be 5.23.0 or later
  release_label = "emr-5.24.1"

  security_configuration = "example"

  # Termination protection is automatically enabled for multiple masters
  # To destroy the cluster, this must be configured to false and applied first
  termination_protection = true

  ec2_attributes {
    # ... other configuration ...

    subnet_id = aws_subnet.example.id
  }

  master_instance_group {
    # ... other configuration ...

    # Master instance count must be set to 3
    instance_count = 3
  }

  # core_instance_group must be configured
  core_instance_group {
    # ... other configuration ...
  }
}

resource "aws_emr_cluster" "fail" {
  # ... other configuration ...

  # EMR version must be 5.23.0 or later
  release_label = "emr-5.24.1"

  # Termination protection is automatically enabled for multiple masters
  # To destroy the cluster, this must be configured to false and applied first
  termination_protection = true

  ec2_attributes {
    # ... other configuration ...

    subnet_id = aws_subnet.example.id
  }

  master_instance_group {
    # ... other configuration ...

    # Master instance count must be set to 3
    instance_count = 3
  }

  # core_instance_group must be configured
  core_instance_group {
    # ... other configuration ...
  }
}