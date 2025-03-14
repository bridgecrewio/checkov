# Vulnerable - no owner and '*' in name
data "aws_ami" "fail1" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Vulnerable - no owner and '?' in name
data "aws_ami" "fail2" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-20.04-amd64-server-202?"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Safe - has owner specified
data "aws_ami" "pass1" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical Ubuntu owner ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server"]  # Even with wildcard, it's safer because owner is specified
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Safe - specific AMI name, no wildcards
data "aws_ami" "pass2" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-20.04-amd64-server-20230517"]  # Specific version
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}