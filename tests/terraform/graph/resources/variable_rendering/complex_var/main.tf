resource "aws_iam_policy" "test" {
  name        = "test"
  description = "test"
  policy      = jsonencode({
    Version = "1970-01-01"
    Statement = [
      {
        Effect   = "Deny"
        Action   = "*"
        Resource = "*"
        Condition = {
          MyCond = {
            "key" = var.ip_list
          }
        }
      },
    ]
  })
}

variable "ip_list" {
  type = list(string)
  default = ["0.0.0.0", "1.1.1.1"]
}