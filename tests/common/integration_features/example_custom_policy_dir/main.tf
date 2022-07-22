
resource "aws_s3_bucket" "b1" {
  bucket = "bucket1"
  tags = {
    owner: "xyz"
  }
}

resource "aws_api_gateway_documentation_version" "untaggable" {

}
