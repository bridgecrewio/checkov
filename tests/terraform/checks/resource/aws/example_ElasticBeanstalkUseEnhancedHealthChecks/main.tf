resource "aws_elastic_beanstalk_environment" "fail" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
}

resource "aws_elastic_beanstalk_environment" "fail2" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = "basic"
  }
}

resource "aws_elastic_beanstalk_environment" "fail3" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "HealthStreamingEnabled"
    value     = "False"
  }

  setting {
    namespace = "guff"
    name      = "SystemType"
    value     = "basic"
  }
}

resource "aws_elastic_beanstalk_environment" "fail4" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "HealthStreamingEnabled"
    resource  = ""
    value     = ""
  }
}


resource "aws_elastic_beanstalk_environment" "pass" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "HealthStreamingEnabled"
    value     = "true"
  }
}

resource "aws_elastic_beanstalk_environment" "pass2" {
  name                   = "beany"
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "HealthStreamingEnabled"
    value     = true
  }
}

locals {
  tags = {
    pike = "permissions"
  }
}

variable "version_label" {
  default = "1.0"
}

variable "wait_for_ready_timeout" {
  default = "20m"
}

variable "solution_stack_name" {
  default = "64bit Amazon Linux 2015.03 v2.0.3 running Go 1.4"
}

variable "tier" {
  default = "WebServer"
}

variable "description" {
  default = "pike is permissions"
}

variable "application" {
  default = "random"
}

variable "elastic_beanstalk_application_name" {
  default = "sato"
}