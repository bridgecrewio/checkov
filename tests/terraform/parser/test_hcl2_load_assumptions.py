import json
import unittest

import hcl2


# This group of tests is used to confirm assumptions about how the hcl2 library parses into json.
# We want to make sure important assumptions are caught if behavior changes.
class TestHCL2LoadAssumptions(unittest.TestCase):
    def test_ternary(self):
        # Ternary and removal of parens are interesting things here
        tf = '''
        resource "aws_instance" "foo" {
          metadata_options {
            http_tokens = (var.metadata_http_tokens_required) ? "required" : "optional"
          }
        }'''
        expect = {
            "resource": [{
                "aws_instance": {
                    "foo": {
                        "metadata_options": [{
                            "http_tokens": ['${var.metadata_http_tokens_required ? "required" : "optional"}']
                        }],
                        "__start_line__": 2,
                        "__end_line__": 6,
                    }
                }
            }]
        }
        self.go(tf, expect)

    def test_tfvars(self):
        tf = '''
        VERSIONING = true
        CHECKOV = "awesome"
        '''
        expect = {
            "VERSIONING": [True],
            "CHECKOV": ["awesome"]
        }
        self.go(tf, expect)

    def test_multiline_function(self):
        tf = '''
        locals {
           a_string = merge(
             local.foo,
             {a="b"}
           )
        }'''
        expect = {
            "locals": [
                {
                    "a_string": ["${merge(local.foo,{'a': 'b'})}"],
                    "__start_line__": 2,
                    "__end_line__": 7,
                }
            ]
        }
        self.go(tf, expect)

    def test_string_with_quotes(self):
        tf = '''
        locals {
           a_string = "Quotes are \\"fun\\"!"
        }'''
        expect = {
            "locals": [
                {
                    "a_string": ["Quotes are \\\"fun\\\"!"],
                    #                        __--
                    #                        |  |
                    #                backslash  quote
                    "__start_line__": 2,
                    "__end_line__": 4,
                }
            ]
        }
        self.go(tf, expect)

    def test_inner_quoting(self):
        tf = '''
        locals {
          evil_strings1 = merge({a="}, evil"})
        }'''
        expect = {
            "locals": [
                {
                    "evil_strings1": ["${merge({'a': '}, evil'})}"],
                    "__start_line__": 2,
                    "__end_line__": 4,
                },
            ]
        }
        self.go(tf, expect)

    def test_merge_with_inner_var(self):
        tf = '''
        resource "aws_s3_bucket" "foo" {
          tags = merge(local.common_tags, local.common_data_tags, {Name = "my-thing-${var.ENVIRONMENT}-${var.REGION}"})
        }'''
        expect = {
            "resource": [
                {
                    "aws_s3_bucket": {
                        "foo": {
                            "tags": ["${merge(local.common_tags,local.common_data_tags,{'Name': 'my-thing-${var.ENVIRONMENT}-${var.REGION}'})}"],
                            "__start_line__": 2,
                            "__end_line__": 4,
                        }
                    }
                }
            ]
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
                        "type": ["${string}"],  # NOTE: wrapped in eval markers
                        "default": ["my_default_value"],
                        "__start_line__": 2,
                        "__end_line__": 5,
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
                        "BLAH": ["a value"],
                        "__start_line__": 2,
                        "__end_line__": 6,
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
                    "INTS": ["${tomap({'a': 1, 'b': 2})}"],  # WHA?? Equals to colons? Okay...
                    "__start_line__": 2,
                    "__end_line__": 4,
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
                        "default": ["-yay"],
                        "__start_line__": 2,
                        "__end_line__": 5,
                    }
                },
                {
                    "input": {
                        "default": ["module-input"],
                        "__start_line__": 7,
                        "__end_line__": 9,
                    }
                }
            ],
            "locals": [
                {
                    "NAME": [{
                        "module-input-bucket": "mapped-bucket-name"
                    }],
                    "TAIL": ["works"],
                    "__start_line__": 11,
                    "__end_line__": 16,
                }
            ],
            "module": [
                {
                    "bucket": {
                        "source": ["./bucket"],
                        "name": ["${var.input}"],  # NOTE: wrapped in eval markers
                        "__start_line__": 18,
                        "__end_line__": 21,
                    }
                }
            ],
            "resource": [
                {
                    "aws_s3_bucket": {
                        "example2": {
                            "bucket": ["${local.NAME[${module.bucket.bucket_name}]}-${local.TAIL}${var.gratuitous_var_default}"],
                            "__start_line__": 23,
                            "__end_line__": 32,
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

    def test_math(self):
        tf = "four = 2 + 2"
        expect = {
            "four": ["${2 + 2}"]
        }
        self.go(tf, expect)

    def test_weird_ternary_string_clipping(self):
        tf = 'bool_string_false = "false" ? "wrong" : "correct"'
        expect = {
            "bool_string_false": ['${"false" ? "wrong" : "correct"}']
        }
        self.go(tf, expect)

    def test_splat_expression(self):
        tf = 'instances = flatten(aws_instance.ubuntu[*].id)'
        expect = {
            'instances': ["${flatten(aws_instance.ubuntu[*].id)}"]
        }
        self.go(tf, expect)
