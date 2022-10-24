# pass

resource "aws_sns_topic" "enabled" {
  name = "example"

  kms_master_key_id = "aws_kms_key.arn"
}

# fail

resource "aws_sns_topic" "default" {
  name = "example"
}
