resource "aws_lambda_permission" "test_lambda_permissions" {
  count         = length([])
  statement_id  = "test_statement_id"
  action        = var.action
  function_name = "my-func"
  principal     = "dumbeldor"
}
