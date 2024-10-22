resource "aws_keyspaces_table" "fail" {
  keyspace_name = aws_keyspaces_keyspace.example.name
  table_name    = "my_table"

  schema_definition {
    column {
      name = "Message"
      type = "ASCII"
    }

    partition_key {
      name = "Message"
    }
  }
}

resource "aws_keyspaces_table" "fail2" {
  keyspace_name = aws_keyspaces_keyspace.example.name
  table_name    = "my_table"

  schema_definition {
    column {
      name = "Message"
      type = "ASCII"
    }

    partition_key {
      name = "Message"
    }
  }
  encryption_specification {
    type="AWS_OWNED_KMS_KEY"
  }
}


resource "aws_keyspaces_table" "fail3" {
  keyspace_name = aws_keyspaces_keyspace.example.name
  table_name    = "my_table"

  schema_definition {
    column {
      name = "Message"
      type = "ASCII"
    }

    partition_key {
      name = "Message"
    }
  }
  encryption_specification {
    kms_key_identifier=aws_kms_key.example.arn
    type="AWS_OWNED_KMS_KEY"
  }
}

resource "aws_keyspaces_table" "pass" {
  keyspace_name = aws_keyspaces_keyspace.example.name
  table_name    = "my_table"

  schema_definition {
    column {
      name = "Message"
      type = "ASCII"
    }

    partition_key {
      name = "Message"
    }
  }
  encryption_specification {
    kms_key_identifier=aws_kms_key.example.arn
    type="CUSTOMER_MANAGED_KMS_KEY"
  }
}
