resource "aws_imagebuilder_component" "fail" {
  data = yamlencode({
    phases = [{
      name = "build"
      steps = [{
        action = "ExecuteBash"
        inputs = {
          commands = ["echo 'hello world'"]
        }
        name      = "example"
        onFailure = "Continue"
      }]
    }]
    schemaVersion = 1.0
  })
  name     = "examplea"
  platform = "Linux"
  version  = "1.0.0"
}

resource "aws_imagebuilder_component" "pass" {
  data = yamlencode({
    phases = [{
      name = "build"
      steps = [{
        action = "ExecuteBash"
        inputs = {
          commands = ["echo 'hello world'"]
        }
        name      = "example"
        onFailure = "Continue"
      }]
    }]
    schemaVersion = 1.0
  })
  kms_key_id = aws_kms_key.test.arn
  name       = "examplea"
  platform   = "Linux"
  version    = "1.0.0"
}