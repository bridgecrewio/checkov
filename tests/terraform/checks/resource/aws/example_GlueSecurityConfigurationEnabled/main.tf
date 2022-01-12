# pass

resource "aws_glue_crawler" "enabled" {
  database_name = "aws_glue_catalog_database.example.name"
  name          = "example"
  role          = "aws_iam_role.example.arn"

  security_configuration = "aws_glue_security_configuration.example.name"
}

resource "aws_glue_dev_endpoint" "enabled" {
  name     = "example"
  role_arn = "aws_iam_role.example.arn"

  security_configuration = "aws_glue_security_configuration.example.name"
}

resource "aws_glue_job" "enabled" {
  name     = "example"
  role_arn = "aws_iam_role.example.arn"

  security_configuration = "aws_glue_security_configuration.example.name"

  command {
    script_location = "s3://aws_s3_bucket.example.bucket/example.py"
  }
}

# fail

resource "aws_glue_crawler" "default" {
  database_name = "aws_glue_catalog_database.example.name"
  name          = "example"
  role          = "aws_iam_role.example.arn"
}

resource "aws_glue_dev_endpoint" "default" {
  name     = "example"
  role_arn = "aws_iam_role.example.arn"
}

resource "aws_glue_job" "default" {
  name     = "example"
  role_arn = "aws_iam_role.example.arn"

  command {
    script_location = "s3://aws_s3_bucket.example.bucket/example.py"
  }
}
