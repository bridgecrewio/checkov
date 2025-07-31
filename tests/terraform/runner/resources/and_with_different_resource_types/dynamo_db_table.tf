provider "aws" {
  region = "us-east-1"
}
resource "aws_dynamodb_table" "example" {
  name = "example-table"
  billing_mode = "PAY_PER_REQUEST" # or "PROVISIONED"
  hash_key = "id" attribute {
  name = "id"
  type = "S" # S = String, N = Number, B = Binary
  }
  tags = {
    AppId               = "APP-1234"
    Billing             = "APP-1234"
    DynatraceMonitoring = true
    EnvironmentType     = "PROD"
    DataClassification  = "HighlyRestricted"
    yor_name            = "example"
    yor_trace           = "d9afaa27-0ffc-49c4-90fa-9c3a7649637f"
  }
} 