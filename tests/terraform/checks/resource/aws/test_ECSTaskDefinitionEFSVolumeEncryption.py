import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ECSTaskDefinitionEFSVolumeEncryption import check
import hcl2

class TestECSTaskDefinitionEFSVolumeEncryption(unittest.TestCase):

    def test_success_no_volume(self):
        hcl_res = hcl2.loads("""
resource "aws_ecs_task_definition" "test" {
  family                = "service"
  container_definitions = file("task-definitions/service.json")

  volume {
    name      = "service-storage"
    host_path = "/ecs/service-storage"
  }

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.availability-zone in [us-west-2a, us-west-2b]"
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecs_task_definition']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_ecs_task_definition" "test" {
  family                = "service"
  container_definitions = file("task-definitions/service.json")

  volume {
    name = "service-storage"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.fs.id
      root_directory          = "/opt/data"
      transit_encryption      = "ENABLED"
      transit_encryption_port = 2999
      authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecs_task_definition']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        
    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_ecs_task_definition" "test" {
  family                = "service"
  container_definitions = file("task-definitions/service.json")

  volume {
    name = "service-storage"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.fs.id
      root_directory          = "/opt/data"
      transit_encryption_port = 2999
      authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecs_task_definition']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_failure_explicit(self):
        hcl_res = hcl2.loads("""
resource "aws_ecs_task_definition" "test" {
  family                = "service"
  container_definitions = file("task-definitions/service.json")

  volume {
    name = "service-storage"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.fs.id
      root_directory          = "/opt/data"
      transit_encryption      = "DISABLED"
      transit_encryption_port = 2999
      authorization_config {
        access_point_id = aws_efs_access_point.test.id
        iam             = "ENABLED"
      }
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecs_task_definition']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
