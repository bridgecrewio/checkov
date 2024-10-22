resource "aws_instance" "pass" {
  ami           = "ami-04169656fea786776"
  instance_type = "t2.nano"
  user_data     = <<EOF
#! /bin/bash
sudo apt-get update
sudo apt-get install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
export AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=FOO
export AWS_SECRET_ACCESS_KEY=bar
export AWS_DEFAULT_REGION=us-west-2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
EOF
  tags = {
    Name = "${local.resource_prefix.value}-ec2"
  }

}
resource "aws_instance" "fail" {
  ami           = "ami-04169656fea786776"
  instance_type = "t2.nano"
  user_data     = <<EOF
#! /bin/bash
sudo apt-get update
sudo apt-get install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
export AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  # checkov:skip=CKV_SECRET_2 test secret
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # checkov:skip=CKV_SECRET_6 test secret
export AWS_DEFAULT_REGION=us-west-2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
EOF
  tags = {
    Name = "${local.resource_prefix.value}-ec2"
  }
}

#resource "aws_launch_configuration" "fail" {
#   name          = "web_config"
#   image_id      = data.aws_ami.ubuntu.id
#   instance_type = "t2.micro"
#   user_data     = <<EOF
# export DATABASE_PASSWORD=\"SomeSortOfPassword\"
# EOF
# }

resource "aws_launch_template" "fail" {

  image_id      = "ami-12345667"
  instance_type = "t2.small"

  user_data = <<EOF
 export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  # checkov:skip=CKV_SECRET_2 test secret
 export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # checkov:skip=CKV_SECRET_6 test secret
 export AWS_DEFAULT_REGION=us-west-2
EOF
}

resource "aws_launch_template" "pass" {
     image_id      = "ami-12345667"
     instance_type = "t2.small"
}

resource "aws_launch_configuration" "fail" {
   name          = "web_config"
   image_id      = data.aws_ami.ubuntu.id
   instance_type = "t2.micro"
   user_data = <<EOF
 export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  # checkov:skip=CKV_SECRET_2 test secret
 export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # checkov:skip=CKV_SECRET_6 test secret
 export AWS_DEFAULT_REGION=us-west-2
EOF
 }

resource "aws_launch_configuration" "pass" {
   name          = "web_config"
   image_id      = data.aws_ami.ubuntu.id
   instance_type = "t2.micro"
 }