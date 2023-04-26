module "submodule" {
  source = "./submodule"
}

resource "aws_subnet" "my_subnet" {
  vpc_id            = module.submodule.vpc_id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "tf-example"
  }
}