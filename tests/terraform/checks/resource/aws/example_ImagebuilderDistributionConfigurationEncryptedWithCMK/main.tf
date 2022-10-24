resource "aws_imagebuilder_distribution_configuration" "fail" {
  name        = "example"
  description = "non empty value"

  distribution {
    ami_distribution_configuration {
      //kms_key_id = ""
      ami_tags = {
        CostCenter = "IT"
      }

      name = "example-{{ imagebuilder:buildDate }}"

      launch_permission {
        user_ids = ["123456789012"]
      }
    }

    region = "us-east-1"
  }
}

resource "aws_imagebuilder_distribution_configuration" "pass" {
  name        = "example"
  description = "non empty value"

  distribution {
    ami_distribution_configuration {
      kms_key_id = aws_kms_key.fail.arn
      ami_tags = {
        CostCenter = "IT"
      }

      name = "example-{{ imagebuilder:buildDate }}"

      launch_permission {
        user_ids = ["123456789012"]
      }
    }

    region = "us-east-1"
  }
}

resource "aws_kms_key" "fail" {}