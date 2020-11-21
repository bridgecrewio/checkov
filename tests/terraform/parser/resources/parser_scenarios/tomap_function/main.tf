locals {
  INTS = tomap({"a" = 1, "b" = 2})
  FLOATS = tomap({"a" = 1.1, "b" = 2.2})
  STRINGS = tomap({"a" = "one", "b" = "two"})
  BOOLS = tomap({"a" = true, "b" = false})

  MIXED_BOOL = tomap({"a" = "foo", "b" = true})
  MIXED_FLOAT = tomap({"a" = "foo", "b" = 1.2})
}