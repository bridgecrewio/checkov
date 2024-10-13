# Pass: authorizationType contains AWS_IAM (Required field)
resource "aws_api_gateway_method" "pass_auth" {
  rest_api_id   = aws_api_gateway_rest_api.pass_auth.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "AWS_IAM"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "pass_auth" {
  name = "example"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Pass: apiKeyRequired set to true
resource "aws_api_gateway_method" "pass_passapikey" {
  rest_api_id   = aws_api_gateway_rest_api.pass_passapikey.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_rest_api" "pass_passapikey" {
  name = "example"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Pass: httpMethod set to POST
resource "aws_api_gateway_method" "pass_httpmethod" {
  rest_api_id   = aws_api_gateway_rest_api.pass_httpmethod.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "pass_passapikey" {
  name = "example"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Pass: Bad config, but no connected aws_api_gateway_rest_api
resource "aws_api_gateway_method" "skipped_noconnect1" {
  rest_api_id   = aws_api_gateway_rest_api.nonexistent.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = false
}

# Fail: Bad aws_api_gateway_method config, bad policy in aws_api_gateway_rest_api_policy
resource "aws_api_gateway_method" "fail1" {
  rest_api_id   = aws_api_gateway_rest_api.fail1.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "fail1" {
  name = "example-rest-api"
}

resource "aws_api_gateway_rest_api_policy" "fail1" {
  rest_api_id = aws_api_gateway_rest_api.fail1.id
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Fail: Bad aws_api_gateway_method config, bad policy in aws_api_gateway_rest_api_policy
resource "aws_api_gateway_method" "fail2" {
  rest_api_id   = aws_api_gateway_rest_api.fail2.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "fail2" {
  name = "example-rest-api"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Fail: Bad aws_api_gateway_method config - missing api_key_required, bad policy in aws_api_gateway_rest_api_policy
resource "aws_api_gateway_method" "fail3" {
  rest_api_id   = aws_api_gateway_rest_api.fail3.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_rest_api" "fail3" {
  name = "example-rest-api"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })
}

# Pass: Bad aws_api_gateway_method config - missing api_key_required, bad policy in aws_api_gateway_rest_api_policy, but PRIVATE
resource "aws_api_gateway_method" "pass_private" {
  rest_api_id   = aws_api_gateway_rest_api.pass_private.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_rest_api" "pass_private" {
  name = "example-rest-api"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })

  endpoint_configuration {
    types            = ["PRIVATE"]
  }
}

# Fail: Bad aws_api_gateway_method config - missing api_key_required, bad policy in aws_api_gateway_rest_api_policy, but Private and Regional
resource "aws_api_gateway_method" "fail4" {
  rest_api_id   = aws_api_gateway_rest_api.fail4.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_rest_api" "fail4" {
  name = "example-rest-api"
  policy      = jsonencode({
    Statement = [
      {
        Effect    = "Allow"
        Action    = "execute-api:Invoke"
        Principal = "*"
      }
    ]
  })

  endpoint_configuration {
    types = ["REGIONAL","PRIVATE"]
  }
}

# Pass: Deny block
resource "aws_api_gateway_method" "pass_deny" {
  rest_api_id   = aws_api_gateway_rest_api.pass_deny.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_rest_api" "pass_deny" {
  name = "example-rest-api"
  policy      = jsonencode({
    Statement = [
      {
        Sid       = "AllowAllForEveryPrincipal"
        Effect    = "Allow"
        Action    = "*"
        Resource  = "*"
        Principal = "*"
      },
      {
        Sid       = "AllowExecuteApiInvokeWithCondition"
        Effect    = "Deny"
        Action    = "execute-api:Invoke"
        Resource  = "*"
        Principal = "*"
      }
    ]
  })
}

# Fail: Separate data block for policy
resource "aws_api_gateway_method" "fail5" {
  rest_api_id   = aws_api_gateway_rest_api.fail5.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "fail5" {
  name = "example-rest-api"
}

data "aws_iam_policy_document" "fail5" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = [aws_api_gateway_rest_api.fail5.execution_arn]
  }
}

resource "aws_api_gateway_rest_api_policy" "fail5" {
  rest_api_id = aws_api_gateway_rest_api.fail5.id
  policy      = data.aws_iam_policy_document.fail5.json
}

# Pass: Separate data block for policy, deny
resource "aws_api_gateway_method" "pass_deny2" {
  rest_api_id   = aws_api_gateway_rest_api.pass_deny2.id
  resource_id   = aws_api_gateway_resource.example.id
  http_method   = "OPTIONS"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_rest_api" "pass_deny2" {
  name = "example-rest-api"
}

data "aws_iam_policy_document" "pass_deny2" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["execute-api:*"]
    resources = ["*"]
  }

  statement {
    effect = "Deny"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["*"]
  }
}

resource "aws_api_gateway_rest_api_policy" "pass_deny2" {
  rest_api_id = aws_api_gateway_rest_api.pass_deny2.id
  policy      = data.aws_iam_policy_document.pass_deny2.json
}
