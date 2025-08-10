
resource "aws_instance" "this" {
  for_each = { for host in var.vmhosts : host.name => host }

  instance_type          = var.instance_type
  key_name               = var.key_name
  private_ip             = each.value.private_ip
  monitoring             = each.value.monitoring
  
  tags = merge(each.value.tags, { Name = each.value.name }, {})

}
