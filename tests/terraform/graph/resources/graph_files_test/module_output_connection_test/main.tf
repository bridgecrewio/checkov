# Parent file with DynamoDB resource policy
# This should connect to the table in the module via module.dynamodb.table_arn

module "dynamodb" {
  source = "./modules/dynamodb"
  
  table_name = "test-table"
}

# Policy WITH conditions - should PASS the security check
resource "aws_dynamodb_resource_policy" "test_policy" {
  resource_arn = module.dynamodb.table_arn
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::123456789012:root"
        }
        Action = "dynamodb:*"
        Resource = module.dynamodb.table_arn
        Condition = {
          StringEquals = {
            "aws:PrincipalOrgID" = "o-xxxxxxxxxx"
          }
        }
      }
    ]
  })
}