resource "aws_iam_role" "pass" {
  name               = "pass_role"
  assume_role_policy = "{\"Version\": \"2012-10-17\", \"Statement\": []}"
  # max_session_duration not set -> defaults to 3600
}

resource "aws_iam_role" "pass_explicit" {
  name                 = "pass_explicit_role"
  assume_role_policy   = "{\"Version\": \"2012-10-17\", \"Statement\": []}"
  max_session_duration = 3600
}

resource "aws_iam_role" "fail" {
  name                 = "fail_role"
  assume_role_policy   = "{\"Version\": \"2012-10-17\", \"Statement\": []}"
  max_session_duration = 43200
}
