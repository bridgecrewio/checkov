resource "aws_lambda_function" "this" {
  count = 0

  function_name                  = "lambda_function_name"
  role                           = ""
  handler                        = ""
  runtime                        = ""
}
