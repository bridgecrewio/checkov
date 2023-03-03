# pass
resource "aws_glacier_vault" "my_archive1" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": "*",
          "Effect": "Deny",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# unknown
resource "aws_glacier_vault" "my_archive1" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": "*",
          "Effect": "Deny",
          "Action": [
             ["glacier:InitiateJob"],
             ["glacier:GetJobOutput"]
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# fail
resource "aws_glacier_vault" "my_archive2" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
           "Principal": { 
            "AWS": [
                "arn:aws:iam::123456789101:role/vault-reader", 
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# fail
resource "aws_glacier_vault" "my_archive3" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": { 
            "AWS": "arn:aws:iam::*:role/vault-reader"
          },
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# fail
resource "aws_glacier_vault" "my_archive4" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
           "Principal": { 
            "AWS": "*"
          },
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# fail
resource "aws_glacier_vault" "my_archive5" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": "*",
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}

# pass
resource "aws_glacier_vault" "my_archive6" {
  name = "MyArchive"

  access_policy = <<EOF
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": "arn:aws:iam::123456789101:role/vault-reader",
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}


resource "aws_glacier_vault" "invalid_json" {
  name = "InvalidJson"

  access_policy = <<EOF
{
    "Version":"2012-10-17"
    "Statement":[
       {
          "Sid": "add-read-only-perm",
          "Principal": "arn:aws:iam::123456789101:role/vault-reader",
          "Effect": "Allow",
          "Action": [
             "glacier:InitiateJob",
             "glacier:GetJobOutput"
          ],
          "Resource": "arn:aws:glacier:eu-west-1:432981146916:vaults/MyArchive"
       }
    ]
}
EOF
}