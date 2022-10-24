resource "aws_dynamodb_table" "basic-dynamodb-table" {
  name           = "test"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "test"
  range_key      = "test"
  attribute {
    name = "test"
    type = "S"
  }

  attribute {
    name = "test"
    type = "S"
  }
  server_side_encryption {
    enabled     = true
    kms_key_arn = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
  }
  point_in_time_recovery {
    enabled = true
  }
  tags = {
    "tag1" = "test"
    "tag2" = "test"
  }
}

resource "aws_autoscaling_group" "example" {
  max_size             = 1
  min_size             = 1
  health_check_type    = "ELB"
  vpc_zone_identifier  = ["arn:aws:vpc:some_vpc"]
  launch_configuration = "test"

  tags = [
            {
                key = "tag1"
                value = "test"
                propagate_at_launch = true
            },
            {
                key = "tag2"
                value = "test"
                propagate_at_launch = true
            },
  ]
}

resource "aws_autoscaling_group" "example2" {
  max_size             = 1
  min_size             = 1
  launch_configuration = "test"

  tag {
      key = "tag1"
      value = "test"
      propagate_at_launch = true
  }
  tag {
      key = "tag2"
      value = "test"
      propagate_at_launch = true
  }
}
