region = "us-west-1"

namespace = "eg"

stage = "test"

name = "s3-user"

s3_actions = ["s3:GetObject"]

s3_resources = ["arn:aws:s3:::cpco-testing-ecs-alb-access-logs/*"]
