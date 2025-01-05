terraform {
  backend "s3" {
    bucket = "example-bucket"
    key    = "path/to/state"
    region = "us-east-1"
    use_lockfile = true
    dynamodb_table = "terraform-locks"
  }
}