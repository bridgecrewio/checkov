# pass

resource "aws_efs_file_system" "enabled" {
  creation_token = "example"

  encrypted = true
}

# fail

resource "aws_efs_file_system" "default" {
  creation_token = "example"
}

resource "aws_efs_file_system" "disabled" {
  creation_token = "example"

  encrypted = false
}
