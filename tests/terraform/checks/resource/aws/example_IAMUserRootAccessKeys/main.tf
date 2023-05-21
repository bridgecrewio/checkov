resource "aws_iam_access_key" "fail" {
    user = "root"
}

resource "aws_iam_access_key" "pass" {
    user = "pike"
}