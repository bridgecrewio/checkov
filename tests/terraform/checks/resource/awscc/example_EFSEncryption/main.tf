resource "awscc_efs_file_system" "pass" {
  file_system_tags = [
    {
      key   = "Name"
      value = "encrypted-efs"
    }
  ]
  encrypted = true
}

resource "awscc_efs_file_system" "fail" {
  file_system_tags = [
    {
      key   = "Name"
      value = "unencrypted-efs"
    }
  ]
  encrypted = false
}

resource "awscc_efs_file_system" "fail2" {
  file_system_tags = [
    {
      key   = "Name"
      value = "default-efs"
    }
  ]
  # encrypted defaults to false
}
