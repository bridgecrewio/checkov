locals {
  INTS = map("a", 1, "b", 2)
  FLOATS = map("a", 1.1, "b", 2.2)
  STRINGS = map("a", "one", "b", "two")
  BOOLS = map("a", true, "b", false)

  MIXED_BOOL = map("a", "foo", "b", true)
  MIXED_FLOAT = map("a", "foo", "b", 1.2)

  ANNOYING_SPLIT = map("this, is", "really, annoying")

  INVALID_ODD_ARGS = map("only one")

  common_tags = map(
    "App", "my_app",
    "Product", "my_product",
    "Team", "my_team",
  )
}