
resource "aws_ami_copy" "fail" {
  name              = "terraform-example"
  description       = "A copy of ami-xxxxxxxx"
  source_ami_id     = "ami-xxxxxxxx"
  source_ami_region = "us-west-1"
  encrypted         = false #default is false
  tags = {
    Name = "HelloWorld"
    test = "failed"
  }
}


resource "aws_ami_copy" "fail2" {
  name              = "terraform-example"
  description       = "A copy of ami-xxxxxxxx"
  source_ami_id     = "ami-xxxxxxxx"
  source_ami_region = "us-west-1"
  tags = {
    Name = "HelloWorld"
    test = "failed"
  }
}


resource "aws_ami_copy" "pass" {
  name              = "terraform-example"
  description       = "A copy of ami-xxxxxxxx"
  source_ami_id     = "ami-xxxxxxxx"
  source_ami_region = "us-west-1"
  encrypted         = true
  tags = {
    Name = "HelloWorld"
    test = "failed"
  }
}
