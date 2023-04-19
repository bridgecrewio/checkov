locals {
  bucket_name = "s3-bucket-${random_pet.this.id}"
}

resource "random_pet" "this" {
  length = 2
}

module "s3_bucket" {
  source = "../../"

  bucket        = local.bucket_name
  force_destroy = true
}

#############################################
# Using packaged function from Lambda module
#############################################

locals {
  package_url = "https://raw.githubusercontent.com/terraform-aws-modules/terraform-aws-lambda/master/examples/fixtures/python3.8-zip/existing_package.zip"
  downloaded  = "downloaded_package_${md5(local.package_url)}.zip"
}

resource "null_resource" "download_package" {
  triggers = {
    downloaded = local.downloaded
  }

  provisioner "local-exec" {
    command = "curl -L -o ${local.downloaded} ${local.package_url}"
  }
}

data "null_data_source" "downloaded_package" {
  inputs = {
    id       = null_resource.download_package.id
    filename = local.downloaded
  }
}

module "lambda_function1" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 1.0"

  function_name = "${random_pet.this.id}-lambda1"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"

  create_package         = false
  local_existing_package = data.null_data_source.downloaded_package.outputs["filename"]
}
