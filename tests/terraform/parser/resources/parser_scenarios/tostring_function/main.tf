locals {
  NUM = tostring(1)
  STRING = tostring("a string")

  # NOTE: These cases should keep the values as string, but they are currently (2020-11-15) converted to
  #       boolean values. This is caused by the str->bool translation happening on a second loop. (The first
  #       correctly converts to a str, the second translates to a bool.)
  #       Desired expected:
  #          "TRUE": ["true"],
  #          "FALSE": ["false"],
  #       Actual is currently:
  #          "TRUE": [true],
  #          "FALSE": [false],
  # TRUE = tostring("true")
  # FALSE = tostring("false")

  INVALID_ARRAY = tostring([])

  INNER_CURLY = tostring("annoying {")
}