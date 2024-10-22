resource "aws_efs_access_point" "pass" {
  file_system_id = aws_efs_file_system.sharedstore.id
  root_directory {
    path=var.root_path
  }
}

variable "root_path" {
    type=string
    default = "/data"
}

resource "aws_efs_access_point" "fail" {
  file_system_id = aws_efs_file_system.sharedstore.id
  root_directory {
    path="/"
  }
}


resource "aws_efs_access_point" "fail2" {
  file_system_id = aws_efs_file_system.sharedstore.id
}