resource "aws_s3_bucket" "single" {
  count  = 1
  bucket = "single"
}

resource "aws_s3_bucket" "multi" {
  count  = 3
  bucket = "multi-${count.index}"
}

# literal index into a single-instance resource
resource "aws_s3_bucket_versioning" "single_literal" {
  bucket = aws_s3_bucket.single[0].id
}

# splat on a single-instance resource can only mean that instance
resource "aws_s3_bucket_versioning" "single_splat" {
  bucket = one(aws_s3_bucket.single[*].id)
}

# literal index must bind to exactly that instance
resource "aws_s3_bucket_versioning" "multi_literal" {
  bucket = aws_s3_bucket.multi[2].id
}

# several literal indexes in one attribute
resource "aws_backup_selection" "multi_literals" {
  resources = [aws_s3_bucket.multi[0].arn, aws_s3_bucket.multi[1].arn]
}

# a splat over several instances is not resolved to a specific instance
resource "aws_s3_bucket_versioning" "multi_splat" {
  bucket = aws_s3_bucket.multi[*].id
}
