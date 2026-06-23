resource "aws_db_instance" "suppressed_ckv_prefix" {
  # checkov:skip=CKV_CUSTOM_a12f9ef1-1234-5678-1234-1234d0225678: suppressed with original CKV prefix (exact match)
  identifier        = "suppressed-ckv-rds"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  publicly_accessible = true
}

resource "aws_db_instance" "suppressed_prefix" {
  # checkov:skip=LETTER_CUSTOM_a12f9ef1-1234-5678-1234-1234d0225678: suppressed
  identifier        = "suppressed-rds"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  publicly_accessible = true
}

resource "aws_db_instance" "wrong_uuid_skip" {
  # checkov:skip=CKV_CUSTOM_ffffffff-ffff-ffff-ffff-ffffffffffff: wrong UUID, should NOT suppress
  identifier        = "wrong-uuid-rds"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  publicly_accessible = true
}

resource "aws_db_instance" "no_skip" {
  identifier        = "no-skip-rds"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  publicly_accessible = true
}
