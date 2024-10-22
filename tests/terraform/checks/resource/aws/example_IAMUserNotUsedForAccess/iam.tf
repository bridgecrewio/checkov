# fail
resource "aws_iam_user" "bad" {
  name = "example"
  path = "/system/"

  tags = {
    tag-key = "tag-value"
  }
}


