# pass
resource "tencentcloud_instance" "default" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"

}

resource "tencentcloud_instance" "positive" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  vpc_id            = tencentcloud_vpc.vpc.id
  subnet_id         = tencentcloud_subnet.subnet.id
}

# failed
resource "tencentcloud_instance" "negative1" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  vpc_id            = tencentcloud_vpc.default.id
  subnet_id         = tencentcloud_subnet.subnet.id
}

resource "tencentcloud_instance" "negative2" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  vpc_id            = tencentcloud_vpc.vpc.id
  subnet_id         = tencentcloud_subnet.default.id
}

resource "tencentcloud_instance" "negative3" {
  instance_name     = "tf-cvm-basic"
  availability_zone = "ap-guangzhou-3"
  vpc_id            = tencentcloud_vpc.default.id
  subnet_id         = tencentcloud_subnet.default.id
}