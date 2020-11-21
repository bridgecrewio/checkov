import json
import unittest

import hcl2


# This group of tests is used to confirm assumptions about how the hcl2 library parses into json.
# We want to make sure important assumptions are caught if behavior changes.
class TestHCL2LoadAssumptions(unittest.TestCase):

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

    def test_map_separators(self):
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

    # from the "maze_of_variables" scenario
    def test_maze_of_variables(self):
        tf = '''
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

    @staticmethod
    def go(tf, expected_result):
        actual_result = hcl2.loads(tf)
        assert actual_result == expected_result, "Results mismatch:\n" \
                                                 "** EXPECTED **\n" \
                                                 f"{json.dumps(expected_result, indent=2)}\n" \
                                                 f"** ACTUAL **\n" \
                                                 f"{json.dumps(actual_result, indent=2)}"
