import unittest

from typing import List, Optional, Tuple

from checkov.terraform import parser
from checkov.terraform.parser import VarBlockMatch as VBM


class TestParserInternals(unittest.TestCase):
    def test_eval_string_to_list(self):
        expected = ["a", "b", "c"]
        assert parser._eval_string('["a", "b", "c"]') == expected

    def test_split_merge_args(self):
        cases: List[Tuple[str, List[str]]] = [
            ("local.one, local.two",
             ["local.one", "local.two"]),
            ("{Tag4 = \"four\"}, {Tag5 = \"five\"}",
             ["{Tag4 = \"four\"}", "{Tag5 = \"five\"}"]),
            ("{a=\"b\"}, {a=[1,2], c=\"z\"}, {d=3}",
             ["{a=\"b\"}", "{a=[1,2], c=\"z\"}", "{d=3}"]),
            ("local.common_tags, merge({Tag4 = \"four\"}, {Tag5 = \"five\"})",
             ["local.common_tags", "merge({Tag4 = \"four\"}, {Tag5 = \"five\"})"]),
            (", ",
             None),
            ("",
             None),
            (", leading_comma",
             ["leading_comma"]),
            ("kinda_maybe_shouldnt_work_but_we_will_roll_with_it, ",        # <-- trailing comma
             ["kinda_maybe_shouldnt_work_but_we_will_roll_with_it"]),
            ("local.one",
             ["local.one"]),
            ('{"a": "}, evil"}',        # bracket inside string, should not be split
             ['{"a": "}, evil"}']),
            ("{'a': '}, evil'}",        # bracket inside string, should not be split
             ["{'a': '}, evil'}"]),     # Note: these happen with native maps (see merge tests)
            ('${merge({\'a\': \'}, evil\'})}',
             ['${merge({\'a\': \'}, evil\'})}']),
            ('local.common_tags,,{\'Tag4\': \'four\'},,{\'Tag2\': \'Dev\'},',
             ["local.common_tags", "{\'Tag4\': \'four\'}", "{\'Tag2\': \'Dev\'}"])
        ]
        for case in cases:
            actual = parser._split_merge_args(case[0])
            assert actual == case[1], f"Case \"{case[0]}\" failed. Expected: {case[1]}  Actual: {actual}"

    def test_find_var_blocks(self):
        cases: List[Tuple[str, List[parser.VarBlockMatch]]] = [
            ("${local.one}",
             [VBM("${local.one}", "local.one")]),
            ("${merge({a=\"b\"}, {a=[1,2], c=\"z\"}, {d=3})}",
             [VBM("${merge({a=\"b\"}, {a=[1,2], c=\"z\"}, {d=3})}",
                  "merge({a=\"b\"}, {a=[1,2], c=\"z\"}, {d=3})")]),
            ("\"string$ ${tomap({key=\"value\"})[key]} are fun\"",
             [VBM("${tomap({key=\"value\"})[key]}", "tomap({key=\"value\"})[key]")]),
            # This case highlights that inner evals should be returned
            ("${filemd5(\"${path.module}/templates/some-file.json\")}",
             [VBM("${path.module}", "path.module")]),
            ("${local.NAME[foo]}-${local.TAIL}${var.gratuitous_var_default}",
             [
                 VBM("${local.NAME[foo]}", "local.NAME[foo]"),
                 VBM("${local.TAIL}", "local.TAIL"),
                 VBM("${var.gratuitous_var_default}", "var.gratuitous_var_default")
             ]),
            ("${tostring(\"annoying {\")}",
             [VBM("${tostring(\"annoying {\")}", "tostring(\"annoying {\")")]),
            ("${this-is-unterminated", []),
            ("${merge({\"a\": \"}, evil\"},{\"b\": \"\\\" , evil\"})}",
             [VBM("${merge({\"a\": \"}, evil\"},{\"b\": \"\\\" , evil\"})}",
                  "merge({\"a\": \"}, evil\"},{\"b\": \"\\\" , evil\"})")]),
            ("$${foo}", []),         # escape interpolation
            ('${merge({\'a\': \'}, evil\'})}',
             [VBM('${merge({\'a\': \'}, evil\'})}', 'merge({\'a\': \'}, evil\'})')]),

            # Ternaries
            ('${var.metadata_http_tokens_required ? "required" : "optional"}',
             [VBM('var.metadata_http_tokens_required', 'var.metadata_http_tokens_required')]),
            ('${1 + 1 == 2 ? "required" : "optional"}',
             [VBM('1 + 1 == 2', '1 + 1 == 2')]),
            ('${true ? "required" : "optional"}',
             [VBM('${true ? "required" : "optional"}', 'true ? "required" : "optional"')]),
            ('${false ? "required" : "optional"}',
             [VBM('${false ? "required" : "optional"}', 'false ? "required" : "optional"')])
        ]
        for case in cases:
            actual = parser._find_var_blocks(case[0])
            assert actual == case[1], f"Case \"{case[0]}\" failed. Expected: {case[1]}  Actual: {actual}"
