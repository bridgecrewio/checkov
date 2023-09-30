## SHOULD PASS: This permission specifies a source_arn, therefore is not globally available.
resource "aws_lambda_permission" "ckv_unittest_pass_source_arn" {
    statement_id  = "AllowMyDemoAPIInvoke"
    action        = "lambda:InvokeFunction"
    function_name = "MyDemoFunction"
    principal     = "apigateway.amazonaws.com"

    # The /*/*/* part allows invocation from any stage, method and resource path
    # within API Gateway REST API.
    source_arn = "${aws_api_gateway_rest_api.MyDemoAPI.execution_arn}/*/*/*"
}

## SHOULD PASS: This permission specifies a source_account, therefore is not globally available.
resource "aws_lambda_permission" "ckv_unittest_pass_source_account" {
    statement_id  = "AllowMyDemoAPIInvoke"
    action        = "lambda:InvokeFunction"
    function_name = "MyDemoFunction"
    principal     = "apigateway.amazonaws.com"

    source_account = "901234678"
}

## SHOULD UNKNOWN: This permission specifies a principal as an account ID.
resource "aws_lambda_permission" "ckv_unittest_unknown_principal" {
    statement_id  = "AllowMyDemoAPIInvoke"
    action        = "lambda:InvokeFunction"
    function_name = "MyDemoFunction"
    principal     = "901234678"
}

## SHOULD FAIL: This allows any serviceprincpal across all accounts to access
resource "aws_lambda_permission" "ckv_unittest_fail" {
    statement_id  = "AllowMyDemoAPIInvoke"
    action        = "lambda:InvokeFunction"
    function_name = "MyDemoFunction"
    principal     = "apigateway.amazonaws.com"
}