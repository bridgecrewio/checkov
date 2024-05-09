resource "aws_s3_bucket" "data_dict" {
  for_each = var.test_dict.bucket
  subnet_id     = each.value
}


resource "aws_s3_bucket" "data_count" {
  count = var.test_count.bucket
#  bucket = data.aws_s3_bucket.data_count[count.index].id
#  aaa = data.aws_s3_bucket.data_count[count.index].bucket
  bbb = data.aws_s3_bucket.data_count[0].bucket
}

resource "aws_s3_bucket" "data" {
  subnet_id     = data.aws_s3_bucket.data.bucket
}
