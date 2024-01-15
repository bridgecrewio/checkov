#fail
resource "aws_s3_bucket" "deprecated" {
  bucket = "bucket"

  policy = <<POLICY
        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Principal": {
                "AWS": [
                "*"
                ]
            },
            "Effect": "Deny",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "*"
            ]
            }
        ]
        }
        POLICY
}

#jsonencode

resource "aws_s3_bucket_policy" "failjsonencode" {
  bucket = "bucket"

  policy = jsonencode({
            "Version": "2012-10-17",
            "Statement": [{
                "Principal": {
                    "AWS": [
                        "*"
                    ]
                },
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [
                    "*"
                ]
            }]
        })
}

resource "aws_s3_bucket_policy" "multi_statement_fail" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                },
                {
                    "Principal": {
                      "AWS": [
                        "*"
                      ]
                    },
                    "Effect": "Deny",
                    "Action": "s3:*",
                    "Resource": [
                        "*"
                    ]
                }
            ]
        }
        POLICY
}

resource "aws_s3_bucket_policy" "fail" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Version": "2012-10-17",
            "Statement": [{
                "Principal": {
                    "AWS": [
                        "*"
                    ]
                },
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [
                    "*"
                ]
            }]
        }
        POLICY
}

resource "aws_s3_bucket" "deprecated2" {
  bucket = "bucket"

  policy = <<POLICY
        {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Principal": "*",
            "Effect": "Deny",
            "Action": "s3:*"
            }
        ]
        }
        POLICY
}

#pass
resource "aws_s3_bucket_policy" "baddata" {
  bucket = "bucket"

  policy = ""
}

resource "aws_s3_bucket_policy" "pass3" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                    "Effect": "Deny"
                }
            ]
        }
        POLICY
}

resource "aws_s3_bucket_policy" "pass4" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "NotAction": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
            ]
        }
        POLICY
}

resource "aws_s3_bucket_policy" "pass2" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
            ]
        }
        POLICY
}

resource "aws_s3_bucket_policy" "pass" {
  bucket = "bucket"

  policy = <<POLICY
        {
            "Id": "Policy1597273448050",
            "Version": "2012-10-17",
            "Statement": {
                    "Sid": "Stmt1597273446725",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Effect": "Deny",
                    "Resource": "arn:aws:s3:::bucket/*",
                    "Principal": {
                        "AWS": "some_arn"
                    }
                }
        }
        POLICY
}

resource "aws_s3_bucket_policy" "pass5" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": {
        "Sid": "Stmt1597273446725",
        "Action": [
            "s3:DeleteObject",
            "s3:DeleteObjectVersion"
        ],
        "Effect": "Deny",
        "Resource": "arn:aws:s3:::bucket/*",
        "Principal": "*"
    }
}
POLICY
}