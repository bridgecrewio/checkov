import unittest
from typing import Any, Optional

import hcl


# This group of tests is used to confirm assumptions about how the hcl2 library parses into json.
# We want to make sure important assumptions are caught if behavior changes.
from checkov.terraform import transforms
from tests.terraform.parser.hcl_load_assumptions_base import HCLLoadAssumptionsBase


class TestHCL1LoadAssumptions(HCLLoadAssumptionsBase, unittest.TestCase):

    def parse(self, terraform: str) -> Any:
        return transforms.transform_hcl1(hcl.loads(terraform))

    def test_heredoc_indented_format(self):
        # Heredoc indented format is not supported in HCL1
        pass

    def test_tomap_separators(self):
        # tomap and built-in map syntax is not supported in HCL1
        pass

    def test_local_block(self):
        # Modifications from base test:
        #  1) `concat` and `local` references wrapped in eval markers
        #  2) HCL2 version remove space inside params in `concat` function
        #  3) Multiple `locals` blocks are merged together
        tf = '''
        locals {
          service_name = "forum"
          owner        = "Community Team"
        }    
        
        locals {
          # Ids for multiple sets of EC2 instances, merged together
          instance_ids = "${concat(aws_instance.blue.*.id, aws_instance.green.*.id)}"
        }
        
        locals {
          # Common tags to be assigned to all resources
          common_tags = {
            Service = "${local.service_name}"
            Owner   = "${local.owner}"
          }
        }'''
        expect = {
            "locals": [
                {
                    "service_name": ["forum"],
                    "owner": ["Community Team"],
                    "instance_ids": ["${concat(aws_instance.blue.*.id, aws_instance.green.*.id)}"],
                    "common_tags": [{
                        "Service": "${local.service_name}",
                        "Owner": "${local.owner}"
                    }]
                }
            ]
        }
        self.go(tf, expect)

    def test_local_blocks(self):
        # Modifications from base test:
        #  1) Multiple `locals` blocks are merged together (can't tell where to split)
        #  2) locals.instance_ids value wrapped in quotes and eval markers
        #  3) locals.common_tags values wrapped in quotes and eval markers
        #  4) There's a space in the `concat` function output
        tf = '''
        locals {
          service_name = "forum"
          owner        = "Community Team"
        }    
        
        locals {
          # Ids for multiple sets of EC2 instances, merged together
          instance_ids = "${concat(aws_instance.blue.*.id, aws_instance.green.*.id)}"
        }
        
        locals {
          # Common tags to be assigned to all resources
          common_tags = {
            Service = "${local.service_name}"
            Owner   = "${local.owner}"
          }
        }'''
        expect = {
            "locals": [
                {
                    "service_name": ["forum"],
                    "owner": ["Community Team"],
                    "instance_ids": ["${concat(aws_instance.blue.*.id, aws_instance.green.*.id)}"],
                    "common_tags": [{
                        "Service": "${local.service_name}",
                        "Owner": "${local.owner}"
                    }]
                }
            ]
        }
        self.go(tf, expect)

    def test_resource_block(self):
        # Modifications from base version:
        #  1) `depends_on` values wrapped in quotes
        tf = '''
        resource "aws_instance" "web" {
          ami           = "ami-a1b2c3d4"
          instance_type = "t2.micro"
          depends_on = ["aws_instance.leader", "module.vpc"]
        }'''
        super().test_resource_block(tf_override=tf)

    def test_module_blocks(self):
        # Modifications from base version:
        #  1) `for_each` isn't supported in HCL 1
        tf = '''
        module "module1" {
          source   = "./bucket"
          name     = "module_bucket"
          BLAH     = "a value"
        }
        module "module2" {
          source   = "./publish_bucket"
          name     = "publish_bucket"
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
                        "source": ["./publish_bucket"],
                        "name": ["publish_bucket"]
                    }
                }
            ]
        }
        self.go(tf, expect)

    def test_maze_of_variables(self):
        # Modifications from base version:
        #  1) Variable type in quotes
        #  2) module.bucket.name value wrapped in quote and eval markers
        tf = '''
        variable "gratuitous_var_default" {
          type = "string"
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
          name     = "${var.input}"
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
        super().test_maze_of_variables(tf_override=tf)

    def test_output_blocks(self, tf_override: str = None):
        # Modifications from base version:
        #  1) Values wrapped in string and eval markers
        tf = '''
        output "role_name" {
          value = "${aws_iam_role.lambda_role.name}"
          description = "This is a role"
        }
        output "arn" {
          value = "${aws_iam_role.lambda_role.arn}"
          sensitive = true
        }
        '''
        super().test_output_blocks(tf_override=tf)

    def test_data_blocks(self):
        super().test_data_blocks()

    def test_all_on_one_line(self):
        # HCL2 parser doesn't like this
        tf = '''
        module "redshift" 
        { source             = "../../../modules/redshift"}
        '''
        expect = {
            'module': [{
                'redshift': {
                    'source': ['../../../modules/redshift']
                }
            }]
        }
        self.go(tf, expect)
