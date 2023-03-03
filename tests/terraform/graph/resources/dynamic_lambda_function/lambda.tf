resource "aws_lambda_function" "lambda" {

  function_name                  = "test"
  role = ""

  dynamic "dead_letter_config" {
    for_each = var.dlc == null ? [] : [var.dlc]
    content {
      target_arn = dead_letter_config.value.target_arn
    }
  }

  dynamic "environment" {
    for_each = var.environment == null ? [] : [var.environment]
    content {
      variables = environment.value.variables
    }
  }
}