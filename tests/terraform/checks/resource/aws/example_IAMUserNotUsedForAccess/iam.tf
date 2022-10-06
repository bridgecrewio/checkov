# pass

resource "aws_iam_user" "null" {
  name = null
}
resource "aws_iam_user" "empty" {
  name = ""
}

# fail
resource "aws_iam_user" "bad" {
  name = "example"
  path = "/system/"

  tags = {
    tag-key = "tag-value"
  }
}


