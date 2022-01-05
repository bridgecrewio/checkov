# pass

resource "aws_kinesis_stream" "enabled" {
  name        = "example"
  shard_count = 1

  encryption_type = "KMS"
}

# fail

resource "aws_kinesis_stream" "default" {
  name        = "example"
  shard_count = 1
}

resource "aws_kinesis_stream" "disabled" {
  name        = "example"
  shard_count = 1

  encryption_type = "NONE"
}
