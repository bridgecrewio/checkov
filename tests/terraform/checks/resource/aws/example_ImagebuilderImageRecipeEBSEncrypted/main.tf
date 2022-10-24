# no blocks
resource "aws_imagebuilder_image_recipe" "pass" {
  #   block_device_mapping {
  #     device_name = "/dev/xvdb"

  #     ebs {
  #     #   encrypted             = true
  #     #   kms_key_id            = aws_kms_key.fail.arn
  #       delete_on_termination = true
  #       volume_size           = 100
  #       volume_type           = "gp2"
  #     }
  #   }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}

#happy path
resource "aws_imagebuilder_image_recipe" "pass2" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    ebs {
      encrypted             = true
      kms_key_id            = aws_kms_key.fail.arn
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}

#no ebs
resource "aws_imagebuilder_image_recipe" "pass3" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    #     ebs {
    #     #   encrypted             = true
    #     #   kms_key_id            = aws_kms_key.fail.arn
    #       delete_on_termination = true
    #       volume_size           = 100
    #       volume_type           = "gp2"
    #     }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}

#nothing set
resource "aws_imagebuilder_image_recipe" "fail" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    ebs {
      #   encrypted             = true
      #   kms_key_id            = aws_kms_key.fail.arn
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}

#no kms key
resource "aws_imagebuilder_image_recipe" "fail2" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    ebs {
      encrypted = true
      #   kms_key_id            = aws_kms_key.fail.arn
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}

#not encrypted
resource "aws_imagebuilder_image_recipe" "fail3" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    ebs {
      #   encrypted             = true
      kms_key_id            = aws_kms_key.fail.arn
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}



data "aws_partition" "current" {}
data "aws_region" "current" {}

resource "aws_kms_key" "fail" {

}


resource "aws_imagebuilder_component" "fail" {
  data = yamlencode({
    phases = [{
      name = "build"
      steps = [{
        action = "ExecuteBash"
        inputs = {
          commands = ["echo 'hello world'"]
        }
        name      = "example"
        onFailure = "Continue"
      }]
    }]
    schemaVersion = 1.0
  })
  name     = "examplea"
  platform = "Linux"
  version  = "1.0.0"
}

resource "aws_imagebuilder_image_recipe" "fail4" {
  block_device_mapping {
    device_name = "/dev/xvdb"

    ebs {
      encrypted             = true
      kms_key_id            = aws_kms_key.fail.arn
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  block_device_mapping {
    device_name = "/dev/xvdc"

    ebs {
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp2"
    }
  }

  component {
    component_arn = aws_imagebuilder_component.fail.arn
  }

  name         = "example"
  parent_image = "arn:${data.aws_partition.current.partition}:imagebuilder:${data.aws_region.current.name}:aws:image/amazon-linux-2-x86/x.x.x"
  version      = "1.0.0"
}


provider "aws" {
  region = "eu-west-1"
}