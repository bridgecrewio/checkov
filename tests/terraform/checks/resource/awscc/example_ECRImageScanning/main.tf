resource "awscc_ecr_repository" "pass" {
  repository_name = "my-secure-repo"
  image_scanning_configuration = {
    scan_on_push = true
  }
}

resource "awscc_ecr_repository" "fail" {
  repository_name = "my-insecure-repo"
  # No image scanning configuration
}

resource "awscc_ecr_repository" "fail2" {
  repository_name = "my-disabled-scanning-repo"
  image_scanning_configuration = {
    scan_on_push = false
  }
}
