output "aws_security_group_public" {
  value = aws_security_group.aws_security_group_public.id
}

output "aws_security_group_private" {
  value = aws_security_group.aws_security_group_private.id
}

output "aws_db_security_group_public" {
  value = aws_db_security_group.aws_db_security_group_public.id
}

output "aws_db_security_group_private" {
  value = aws_db_security_group.aws_db_security_group_private.id
}

output "aws_redshift_security_group_public" {
  value = aws_redshift_security_group.aws_redshift_security_group_public.id
}


output "aws_redshift_security_group_private" {
  value = aws_redshift_security_group.aws_redshift_security_group_private.id
}

output "aws_elasticache_security_group_public" {
  value = aws_elasticache_security_group.aws_elasticache_security_group_public.id
}

output "aws_elasticache_security_group_private" {
  value = aws_elasticache_security_group.aws_elasticache_security_group_private.id
}