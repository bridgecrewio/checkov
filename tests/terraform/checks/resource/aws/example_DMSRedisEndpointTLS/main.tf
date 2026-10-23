# PASS: Redis endpoint with explicit ssl-encryption
resource "aws_dms_endpoint" "pass_ssl_encryption" {
  endpoint_id   = "redis-pass-ssl"
  endpoint_type = "target"
  engine_name   = "redis"

  redis_settings {
    auth_type             = "auth-token"
    auth_user_name        = "myuser"
    auth_password         = "mypassword"
    server_name           = "redis.example.com"
    port                  = 6379
    ssl_security_protocol = "ssl-encryption"
  }
}

# PASS: Redis endpoint without ssl_security_protocol (AWS defaults to ssl-encryption)
resource "aws_dms_endpoint" "pass_default_ssl" {
  endpoint_id   = "redis-pass-default"
  endpoint_type = "target"
  engine_name   = "redis"

  redis_settings {
    auth_type      = "auth-token"
    auth_user_name = "myuser"
    auth_password  = "mypassword"
    server_name    = "redis.example.com"
    port           = 6379
  }
}

# PASS: non-Redis endpoint (auto-pass)
resource "aws_dms_endpoint" "pass_mysql" {
  endpoint_id   = "mysql-pass"
  endpoint_type = "source"
  engine_name   = "mysql"
  server_name   = "mysql.example.com"
  port          = 3306
  username      = "admin"
  password      = "password"
}

# FAIL: Redis endpoint with plaintext
resource "aws_dms_endpoint" "fail_plaintext" {
  endpoint_id   = "redis-fail-plaintext"
  endpoint_type = "target"
  engine_name   = "redis"

  redis_settings {
    auth_type             = "auth-token"
    auth_user_name        = "myuser"
    auth_password         = "mypassword"
    server_name           = "redis.example.com"
    port                  = 6379
    ssl_security_protocol = "plaintext"
  }
}
