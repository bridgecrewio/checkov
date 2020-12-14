import abc
import json
from typing import Any


class HCLLoadAssumptionsBase:
    @abc.abstractmethod
    def parse(self, terraform: str) -> Any:
        raise NotImplementedError

    def go(self, tf, expected_result):
        actual_result = self.parse(tf)
        assert actual_result == expected_result, "Results mismatch:\n" \
                                                 "** EXPECTED **\n" \
                                                 f"{json.dumps(expected_result, indent=2)}\n" \
                                                 f"** ACTUAL **\n" \
                                                 f"{json.dumps(actual_result, indent=2)}"

    def test_empty(self):
        self.go("", {})

    def test_tfvars(self):
        tf = '''
        REGION = "us-east-1"
        ACCOUNT_ID = "0123456789"
        DRY_RUN = "0"
        TEST_MODE = "1"
        '''
        expect = {
          "REGION": ["us-east-1"],
          "ACCOUNT_ID": ["0123456789"],
          "DRY_RUN": ["0"],
          "TEST_MODE": ["1"]
        }
        self.go(tf, expect)

    def test_single_attribute(self):
        tf = 'foo = "bar baz"'
        expect = {
          "foo": ["bar baz"]
        }
        self.go(tf, expect)

    def test_variable_block(self):
        tf = '''
        variable "my_var" {
          type = string
          default = "my_default_value"
        }'''
        expect = {
            "variable": [
                {
                    "my_var": {
                        "type": ["${string}"],              # NOTE: wrapped in eval markers
                        "default": ["my_default_value"]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_variable_blocks(self):
        tf = '''
        variable "var1" {
          default = "1"
        }
        variable "var2" {
          default = "2"
        }
        variable "var3" {}'''
        expect = {
            "variable": [
                {
                    "var1": {
                        "default": ["1"]
                    }
                },
                {
                    "var2": {
                        "default": ["2"]
                    }
                },
                {
                    "var3": {}
                }
            ]
        }
        self.go(tf, expect)

    def test_resource_block(self, tf_override: str = None):
        tf = tf_override if tf_override else '''
        resource "aws_instance" "web" {
          ami           = "ami-a1b2c3d4"
          instance_type = "t2.micro"
          depends_on = [aws_instance.leader, module.vpc]
        }'''
        expect = {
            "resource": [
                {
                    "aws_instance": {
                        "web": {
                            "ami": ["ami-a1b2c3d4"],
                            "instance_type": ["t2.micro"],
                            "depends_on": [["${aws_instance.leader}", "${module.vpc}"]]
                        }
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_resource_blocks(self):
        tf = '''
        resource "aws_s3_bucket" "bucket1" {
          bucket = "bucket-one"
        }
        resource "aws_s3_bucket" "bucket2" {
          bucket = "bucket-two"
        }
        resource "aws_instance" "web" {
          ami               = "${var.ami}"
          count             = 2
          source_dest_check = false
        
          connection {
            user = "root"
          }
        }
        '''
        expect = {
            "resource": [
                {
                    "aws_s3_bucket": {
                        "bucket1": {
                            "bucket": ["bucket-one"]
                        }
                    }
                },
                {
                    "aws_s3_bucket": {
                        "bucket2": {
                            "bucket": ["bucket-two"]
                        }
                    }
                },
                {
                    "aws_instance": {
                        "web": {
                            "ami": ["${var.ami}"],
                            "count": [2],
                            "source_dest_check": [False],
                            "connection": [
                                {
                                    "user": ["root"]
                                }
                            ]
                        }
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_module_block(self):
        tf = '''
        module "bucket" {
          source   = "./bucket"
          name     = "module_bucket"
          BLAH     = "a value"
        }'''
        expect = {
            "module": [
                {
                    "bucket": {
                        "source": ["./bucket"],
                        "name": ["module_bucket"],
                        "BLAH": ["a value"]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_module_blocks(self):
        tf = '''
        module "module1" {
          source   = "./bucket"
          name     = "module_bucket"
          BLAH     = "a value"
        }
        module "module2" {
          for_each = toset(["assets", "media"])
          source   = "./publish_bucket"
          name     = "${each.key}_bucket"
        }
        '''
        expect = {
            "module": [
                {
                    "module1": {
                        "source": ["./bucket"],
                        "name": ["module_bucket"],
                        "BLAH": ["a value"]
                    }
                },
                {
                    "module2": {
                        "for_each": ["${toset(['assets', 'media'])}"],
                        "source": ["./publish_bucket"],
                        "name": ["${each.key}_bucket"]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_local_blocks(self, expect_override=None):
        tf = '''
        locals {
          service_name = "forum"
          owner        = "Community Team"
        }    
        
        locals {
          # Ids for multiple sets of EC2 instances, merged together
          instance_ids = concat(aws_instance.blue.*.id, aws_instance.green.*.id)
        }
        
        locals {
          # Common tags to be assigned to all resources
          common_tags = {
            Service = local.service_name
            Owner   = local.owner
          }
        }'''
        expect = expect_override if expect_override else {
            "locals": [
                {
                    "service_name": ["forum"],
                    "owner": ["Community Team"]
                },
                {
                    "instance_ids": ["${concat(aws_instance.blue.*.id,aws_instance.green.*.id)}"]
                },
                {
                    "common_tags": [{
                        "Service": "${local.service_name}",
                        "Owner": "${local.owner}"
                    }]
                }
            ]
        }
        self.go(tf, expect)

    def test_provider_block(self):
        tf = '''
        provider "aws" {
          region = "us-east-1"
        
          assume_role {
            role_arn     = "arn:aws:iam::0123456789:role/MyCoolRole"
            session_name = "tf_deploy"
          }
        }'''
        expect = {
            "provider": [
                {
                    "aws": {
                        "region": ["us-east-1"],
                        "assume_role": [
                            {
                                "role_arn": ["arn:aws:iam::0123456789:role/MyCoolRole"],
                                "session_name": ["tf_deploy"]
                            }
                        ]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_data_blocks(self):
        tf = '''
        data "aws_ami" "example" {
          most_recent = true
        
          owners = ["self"]
          tags = {
            Name   = "app-server"
            Tested = "true"
          }
        }'''
        expect = {
            "data": [
                {
                    "aws_ami": {
                        "example": {
                            "most_recent": [True],
                            "owners": [["self"]],
                            "tags": [
                                {
                                    "Name": "app-server",
                                    "Tested": "true"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_output_blocks(self, tf_override: str = None):
        tf = tf_override if tf_override else '''
        output "role_name" {
          value = aws_iam_role.lambda_role.name
          description = "This is a role"
        }
        output "arn" {
          value = aws_iam_role.lambda_role.arn
          sensitive = true
        }
        '''
        expect = {
            "output": [
                {
                    "role_name": {
                        "value": ["${aws_iam_role.lambda_role.name}"],
                        "description": ["This is a role"]
                    }
                },
                {
                    "arn": {
                        "value": ["${aws_iam_role.lambda_role.arn}"],
                        "sensitive": [True]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_raw_assignment(self):
        tf = 'my_var = "my_value"\n'
        expect = {
            "my_var": ["my_value"]
        }
        self.go(tf, expect)

    def test_raw_assignment_true_string(self):
        tf = 'my_var = "true"\n'
        expect = {
            "my_var": ["true"]
        }
        self.go(tf, expect)

    def test_raw_assignment_false_string(self):
        tf = 'my_var = "false"\n'
        expect = {
            "my_var": ["false"]
        }
        self.go(tf, expect)

    def test_raw_assignment_1_string(self):
        tf = 'my_var = "1"\n'
        expect = {
            "my_var": ["1"]
        }
        self.go(tf, expect)

    def test_raw_assignment_0_string(self):
        tf = 'my_var = "0"\n'
        expect = {
            "my_var": ["0"]
        }
        self.go(tf, expect)

    def test_heredoc_format(self):
        tf = '''
block {
  value = <<EOT
hello
world
EOT
}
        '''
        expect = {
            "block": [
                {
                    "value": ["hello\nworld"]
                }
            ]
        }
        self.go(tf, expect)

    def test_heredoc_indented_format(self):
        tf = '''
block {
  value = <<-EOT
  hello
    world
  EOT
}
        '''
        expect = {
            "block": [
                {
                    "value": ["hello\n  world"]
                }
            ]
        }
        self.go(tf, expect)

    def test_tomap_separators(self):
        tf = '''
        locals {
          INTS = tomap({"a" = 1, "b" = 2})
        }'''
        expect = {
            "locals": [
                {
                    "INTS": ["${tomap({'a': 1, 'b': 2})}"]          # WHA?? Equals to colons? Okay...
                }
            ]
        }
        self.go(tf, expect)

    def test_map_separators(self):
        tf = '''
        locals {
          INTS = "${map("a",1,"b",2)}"
        }'''
        expect = {
            "locals": [
                {
                    "INTS": ["${map(\"a\",1,\"b\",2)}"]
                }
            ]
        }
        self.go(tf, expect)

    # from the "maze_of_variables" scenario
    def test_maze_of_variables(self, tf_override: str = None):
        tf = tf_override if tf_override else '''
        variable "gratuitous_var_default" {
          type = string
          default = "-yay"
        }

        variable "input" {
          default = "module-input"
        }
         
        locals {
          NAME = {
            "module-input-bucket" = "mapped-bucket-name"
          }
          TAIL = "works"
        }
          
        module "bucket" {
          source   = "./bucket"
          name     = var.input
        }
        
        resource "aws_s3_bucket" "example2" {
          #             resolves to: mapped-bucket-name
          #             |            resolves to: module-input-bucket
          #             |            |                              resolves to: works
          #             |            |                              |           resolves to: -yay
          #             |            |                              |           |
          #             v            v                              v           v
          bucket = "${local.NAME[${module.bucket.bucket_name}]}-${local.TAIL}${var.gratuitous_var_default}"
          # final result: mapped-bucket-name-works-yay
        }'''
        expect = {
            "variable": [
                {
                    "gratuitous_var_default": {
                        "type": ["${string}"],              # NOTE: wrapped in eval markers
                        "default": ["-yay"]
                    }
                },
                {
                    "input": {
                        "default": ["module-input"]
                    }
                }
            ],
            "locals": [
                {
                    "NAME": [{
                        "module-input-bucket": "mapped-bucket-name"
                    }],
                    "TAIL": ["works"]
                }
            ],
            "module": [
                {
                    "bucket": {
                        "source": ["./bucket"],
                        "name": ["${var.input}"]            # NOTE: wrapped in eval markers
                    }
                }
            ],
            "resource": [
                {
                    "aws_s3_bucket": {
                        "example2": {
                            "bucket": ["${local.NAME[${module.bucket.bucket_name}]}-${local.TAIL}${var.gratuitous_var_default}"]
                        }
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_hcl1_map_with_colons(self):
        tf = '''
        output "ebs_sizes" {
          value = {
            "x" : 600,
            "y" : 350,
            "z" : 350,
            "xx" : 200
          }
        }'''
        expect = {
            "output": [
                {
                    "ebs_sizes": {
                        "value": [
                            {
                                "x": 600,
                                "y": 350,
                                "z": 350,
                                "xx": 200
                            }
                        ]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_lb_with_condition_block(self):
        tf = '''
        resource "aws_lb_listener_rule" "kong_rule" {
          listener_arn = "${aws_lb_listener.kong_lb_listener.arn}"
          priority     = 100
        
          action {
            type             = "forward"
            target_group_arn = "${aws_lb_target_group.kong_lb_target_group.0.arn}"
          }
        
          condition {
            path_pattern {
              values = ["/*"]
            }
          }
        }
        '''
        expect = {
            "resource": [
                {
                    'aws_lb_listener_rule': {
                        'kong_rule': {
                            'listener_arn': ['${aws_lb_listener.kong_lb_listener.arn}'],
                            'priority': [100],
                            'action': [{
                                'type': ['forward'],
                                'target_group_arn': ['${aws_lb_target_group.kong_lb_target_group.0.arn}']
                            }],
                            'condition': [{
                                'path_pattern': [{
                                    'values': [['/*']]
                                }]
                            }]
                        }
                    }
                }
            ]
        }
        self.go(tf, expect)