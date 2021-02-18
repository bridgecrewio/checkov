module "mydb" {
  source           = "../../../modules/db"
  DB_INSTANCE_TYPE = "${var.DB_INSTANCE_TYPE}"
  ENGINE_VERSION   = "${var.ENGINE_VERSION}"
  ENCRYPTED        = "${var.ENCRYPTED}"
}