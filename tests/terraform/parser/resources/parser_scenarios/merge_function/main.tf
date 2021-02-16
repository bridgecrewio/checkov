locals {
  common_tags = {
    Tag1 = "one"
    Tag2 = "two"
  }
  common_data_tags = {
    Tag3 = "three"
  }

  local_to_local = merge(local.common_tags, local.common_data_tags)
  local_to_manual = merge(local.common_tags, {Tag4 = "four"})
  local_local_manual = merge(local.common_tags, local.common_data_tags, {Name = "Bob"})
  manual_to_local = merge({Tag4 = "four"}, local.common_tags)
  manual_to_manual = merge({Tag4 = "four"}, {Tag5="five"})

  nested = merge(local.common_tags, merge({Tag4 = "four"}, {Tag5 = "five"}))

  doc_example1 = merge({a="b", c="d"}, {e="f", c="z"})
  doc_example2 = merge({a="b"}, {a=[1,2], c="z"}, {d=3})    # Note: 3 args

  evil_strings1 = merge({a="}, evil"})
  # The HCL parser does something really weird with this case turning the inner quote into (python string):
  #   ${merge({\'b\': \'\\\\" , evil\'})}
  # This seems wrong to me, so I'm skipping for the moment. Expended emitted data is:
  #   "evil_strings2": [
  #     {
  #       "b": "\" , evil"
  #     }
  #   ],
//  evil_strings2 = merge({b="\" , evil"})

  one_arg_local = merge(local.common_tags)
  one_arg_manual = merge({Tag4 = "four"})

  multiline = merge(
    local.common_tags,
    {Tag4 = "four"},
    {Tag2="multiline_tag2"}
  )

  static1 = "one"
  static2 = "two"
}

resource "aws_something" "something" {
  #
  tags = merge(local.common_tags, local.common_data_tags, {Name = "Bob-${local.static1}-${local.static2}"})
}