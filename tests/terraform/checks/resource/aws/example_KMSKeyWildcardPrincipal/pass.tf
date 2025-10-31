resource "aws_kms_key" "pass_0" {
  description = "description"
  policy      = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
POLICY  
}

resource "aws_kms_key" "pass_1" {
  description = "description"
  policy      = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": {
        "AWS": "*"
      },
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
POLICY  
}

resource "aws_kms_key" "pass_2" {
  description = "description"
  policy      = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "foo",
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
POLICY  
}

resource "aws_kms_key" "pass_3" {
  description = "description"
  policy      = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": ["foo","bar"],
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
POLICY  
}

resource "aws_kms_key" "pass_4" {
  description             = "description"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "key-default-1",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": "kms:*",
      "Resource": "*",
      "Condition": {
         "Bool": { "aws:MultiFactorAuthPresent": "true" }
       }
    },
    {
      "Sid": "RestrictWildcardPrincipalToAccount",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "kms:*",
      "Resource": "*",
      "Condition": {
         "StringEquals": {
           "kms:CallerAccount": "111122223333"
         }
       }
    }
  ]
}
POLICY
}
