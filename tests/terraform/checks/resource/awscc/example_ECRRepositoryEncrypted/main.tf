
resource "awscc_ecr_repository" "fail" {
  repository_name      = "fail"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration = {
    scan_on_push = true
  }

}

resource "awscc_ecr_repository" "pass" {
  repository_name      = "pass"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration = {
    scan_on_push = true
  }
  encryption_configuration = {
    encryption_type = "KMS"
  }

}
