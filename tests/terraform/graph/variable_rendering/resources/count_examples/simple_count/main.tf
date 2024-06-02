
# Expected resources:
#    module.simple[0].aws_s3_bucket_object.this_file

# Actual resources:
#    NONE
module "simple" {
  source   = "./simple"
  count = 1
}