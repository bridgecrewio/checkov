import unittest

from detect_secrets.util.code_snippet import CodeSnippet

from checkov.secrets.parsers.json.multiline_parser import json_multiline_parser


class TestMultilineParserJson(unittest.TestCase):
	def setUp(self) -> None:
		self.json_parser = json_multiline_parser

	def test_is_object_start(self):
		examples = [
			(True,  '   {'),
			(True,  '   {	\n'),
			(True,  '		{'),
			(True,  '{'),
			(True,  '"key": {'),
			(True,  '}, {'),
			(False, '"key": {}'),
			(False, '"key": { }'),
			(False, '"key": {	},	'),
			(False, '{ "key": "value" }'),
			(False, '"key": { "key2": "value2", "key3": "value3" }, '),
			(False, '"key": "value" }'),
			(False, '	}, { "key":  '),  # is not supported
			(False, '}'),
			(False, '		}'),
			(False, '"key": 1, '),
			(False, '[1,2], ['),
			(False, '[1,2], '),
		]

		for ans, line in examples:
			assert ans == self.json_parser.is_object_start(line)

	def test_is_object_end(self):
		examples = [
			(True,  '}'),
			(True,  '		}'),
			(True,  '   }'),
			(True,  '	},'),
			(True,  '}]}, '),
			(True,  '"key": "value" }'),
			(True,  '"key": "value" } , '),
			(True,  '}, {'),
			(False,  '"key": {}'),
			(False,  '"key": { }'),
			(False,  '"key": {	},	'),
			(True,  '	}, { "key": "value",'),
			(False, '"key": { "key2": "value2", "key3": "value3" }, '),
			(False, '"key": {'),
			(False, '{'),
			(False, '		{'),
			(False, '"key": 1, '),
			(False, '[1,2], '),
		]

		for ans, line in examples:
			assert ans == self.json_parser.is_object_end(line)

	def test_lines_in_same_object1(self):
		# Please notice that additional logic required to determine for non-sequential lines,
		# see EntropyKeywordCombinator.analyze_multiline() function for example.
		# In the context of the tested function, 2 lines are treated as sequential.
		raw_context_example = CodeSnippet(
			snippet=[
				'  conf_list_of_dicts": [',
				'    {',
				'      "name": "TEST_PASSWORD_1",',
				'      "value": "some secret",',
				'      "desc": "still same obj",',
				'      "type": 1',
				'    }',
				'  ],',
				'  "conf_dict": {',
				'    "name": "TEST_PASSWORD_1",',
				'    "value": "some secret",'
			],
			start_line=5,
			target_index=5
		)
		examples = [
			# index of rows in the context compared to the target row, which is:
			# '      "type": 1'
			(True, 1, raw_context_example),
			(True, 2, raw_context_example),
			(True, 3, raw_context_example),
			(True, 4, raw_context_example),
			(True, 6, raw_context_example),
		]

		for res, i, raw_context in examples:
			assert res == self.json_parser.consecutive_lines_in_same_object(
				raw_context=raw_context, other_line_idx=i)

	def test_lines_in_same_object2(self):

		raw_context_example = CodeSnippet(
			snippet=[
				'  , {',
				'      "value": "some secret",',
				'    }],',
				'  "conf_dict": {',
				'    "name": {} ',
				'    "value": { "key2": "value2", "key3": "value3" }",'
			],
			start_line=2,
			target_index=1
		)

		examples = [
			# index of rows in the context compared to the target row, which is:
			# '      "value": "some secret"'
			(False, 0, raw_context_example),
			(True, 2, raw_context_example),
			(True, 3, raw_context_example),
		]

		for res, i, raw_context in examples:
			assert res == self.json_parser.consecutive_lines_in_same_object(
				raw_context=raw_context, other_line_idx=i)

	def test_lines_in_same_object3(self):
		raw_context_example = CodeSnippet(
			snippet=[
				'  , {',
				'      "value": "some secret",',
				'    }],',
				'  "conf_dict": {',
				'    "name": {} ',
				'    "value": { ',
				'  	 	"key2": "value2", ',
				'    	"value": { "key2": "value2", "key3": "value3" }, ',
			],
			start_line=2,
			target_index=5
		)

		examples = [
			# index of rows in the context compared to the target row, which is:
			# '    "name": {} '
			(True, 4, raw_context_example),
			(False, 6, raw_context_example),
		]

		for res, i, raw_context in examples:
			assert res == self.json_parser.consecutive_lines_in_same_object(
				raw_context=raw_context, other_line_idx=i)
