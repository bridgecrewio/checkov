module "child" {
  count  = 2
  source = "./child"
}

resource "aws_s3_bucket_versioning" "literal" {
  bucket = module.child[0].id
}

# the literal index of a resource passed to a module has to bind to exactly that instance
resource "aws_s3_bucket" "passed" {
  count  = 3
  bucket = "passed"
}

module "takes_input" {
  source    = "./takes_input"
  bucket_id = aws_s3_bucket.passed[1].id
}

module "outer" {
  source    = "./outer"
  bucket_id = aws_s3_bucket.passed[2].id
}

# the string in the function survives rendering, the reference in it is still a real one
locals {
  passed_id = nonsensitive(sensitive("${aws_s3_bucket.passed[1].id}"))
}

resource "aws_s3_bucket_versioning" "through_local" {
  bucket = local.passed_id
}
