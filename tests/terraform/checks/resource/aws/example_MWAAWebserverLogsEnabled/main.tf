resource "aws_mwaa_environment" "pass" {
  dag_s3_path        = "dags/"
  execution_role_arn = "aws_iam_role.example.arn"

  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "DEBUG"
    }

    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  name = "example"

   network_configuration {
    security_group_ids = ["aws_security_group.example.id"]
    subnet_ids         = "aws_subnet.private[*].id"
  }

  source_bucket_arn = "aws_s3_bucket.example.arn"
}

resource "aws_mwaa_environment" "fail_false" {
  dag_s3_path        = "dags/"
  execution_role_arn = "aws_iam_role.example.arn"

  logging_configuration {
    webserver_logs {
      enabled   = false
      log_level = "CRITICAL"
    }
  }

  name = "example"

  network_configuration {
    security_group_ids = ["aws_security_group.example.id"]
    subnet_ids         = "aws_subnet.private[*].id"
  }

  source_bucket_arn = "aws_s3_bucket.example.arn"
}


resource "aws_mwaa_environment" "fail" {
  dag_s3_path        = "dags/"
  execution_role_arn = "aws_iam_role.example.arn"


  name = "example"

  network_configuration {
    security_group_ids = ["aws_security_group.example.id"]
    subnet_ids         = "aws_subnet.private[*].id"
  }

  source_bucket_arn = "aws_s3_bucket.example.arn"
}
