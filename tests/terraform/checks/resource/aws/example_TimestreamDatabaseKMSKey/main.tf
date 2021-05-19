# pass

resource "aws_timestreamwrite_database" "enabled" {
  database_name = "timestream"

  kms_key_id = var.kms_key_id
}

# failure

resource "aws_timestreamwrite_database" "default" {
  database_name = "timestream"
}
