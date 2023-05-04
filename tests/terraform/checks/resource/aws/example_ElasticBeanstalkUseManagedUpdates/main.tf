resource "aws_elastic_beanstalk_environment" "fail" {
  name                   = module.this.id
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
}

resource "aws_elastic_beanstalk_environment" "fail2" {
  name                   = module.this.id
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name      = "ManagedActionsEnabled"
    value     = "false"
  }
}


resource "aws_elastic_beanstalk_environment" "pass" {
  name                   = module.this.id
  application            = var.elastic_beanstalk_application_name
  description            = var.description
  tier                   = var.tier
  solution_stack_name    = var.solution_stack_name
  wait_for_ready_timeout = var.wait_for_ready_timeout
  version_label          = var.version_label
  tags                   = local.tags
  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name      = "ManagedActionsEnabled"
    value     = "true"
  }
}