Resources by Address:

File: /main.tf:21-24
- aws_s3_bucket_object.this_file_2
  - Expected `__provider_address__` == "aws.default"
  - Result: aws.default

File: /nesting/main.tf:36-41
- module.level1.aws_s3_bucket_object.this_other_file
  - Expected `__provider_address__` == "module.level1.aws.default"
  - Result: aws.default


File: /nesting/nesting_l2/main.tf:2-5
- module.level1.module.level2.aws_s3_bucket_object.this_file_2
  - Expected: `__provider_address__` == "module.level1.aws.default"
  - Result: __provider_address__ does not exist

File: /nesting/nesting_l2_2/main.tf:2-5
- module.level1.module.level2_2.aws_s3_bucket_object.this_file_2
  - Expected: `__provider_address__` == "module.level1.aws.eu_west"
  - Result: aws.eu_west

File: /nesting_2/main.tf:2-5
- module.level1_2.aws_s3_bucket_object.this_file_2
  - Expected: `__provider_address__` == "aws.default"
  - Result: aws.default