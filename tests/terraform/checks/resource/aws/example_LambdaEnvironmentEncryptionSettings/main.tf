resource "aws_lambda_function" "fail" {
  function_name                  = var.function_name
  role                           = aws_iam_role.lambda-messageprocessor.arn
  runtime                        = "python3.6"
  handler                        = "handler.lambda_handler"
  filename                       = data.archive_file.notify.output_path
  source_code_hash               = data.archive_file.notify.output_base64sha256
  reserved_concurrent_executions = var.concurrency
  tracing_config {
    mode = "PassThrough"
  }
  environment {
    test = "true"
  }
}

resource "aws_lambda_function" "failkmsnovars" {
  function_name                  = var.function_name
  role                           = aws_iam_role.lambda-messageprocessor.arn
  runtime                        = "python3.6"
  handler                        = "handler.lambda_handler"
  filename                       = data.archive_file.notify.output_path
  source_code_hash               = data.archive_file.notify.output_base64sha256
  reserved_concurrent_executions = var.concurrency
  tracing_config {
    mode = "PassThrough"
  }
  kms_key_arn = aws_kms_key.anyoldguff.arn
}

resource "aws_lambda_function" "ignore" {
  function_name                  = var.function_name
  role                           = aws_iam_role.lambda-messageprocessor.arn
  runtime                        = "python3.6"
  handler                        = "handler.lambda_handler"
  filename                       = data.archive_file.notify.output_path
  source_code_hash               = data.archive_file.notify.output_base64sha256
  reserved_concurrent_executions = var.concurrency
  tracing_config {
    mode = "PassThrough"
  }
}

resource "aws_lambda_function" "pass" {
  function_name                  = var.function_name
  role                           = aws_iam_role.lambda-messageprocessor.arn
  runtime                        = "python3.6"
  handler                        = "handler.lambda_handler"
  filename                       = data.archive_file.notify.output_path
  source_code_hash               = data.archive_file.notify.output_base64sha256
  reserved_concurrent_executions = var.concurrency
  tracing_config {
    mode = "PassThrough"
  }
  environment {
    test = "true"
  }
  kms_key_arn = aws_kms_key.anyoldguff.arn
}

resource "aws_lambda_function" "failasempty" {
  function_name                  = var.function_name
  role                           = aws_iam_role.lambda-messageprocessor.arn
  runtime                        = "python3.6"
  handler                        = "handler.lambda_handler"
  filename                       = data.archive_file.notify.output_path
  source_code_hash               = data.archive_file.notify.output_base64sha256
  reserved_concurrent_executions = var.concurrency
  tracing_config {
    mode = "PassThrough"
  }
  kms_key_arn = ""
}
