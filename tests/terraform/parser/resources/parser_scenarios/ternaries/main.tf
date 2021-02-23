locals {
  a     = "a"
  b     = "b"
  empty = ""

  bool_true  = true ? "correct" : "wrong"
  bool_false = false ? "wrong" : "correct"

//  local_true = true
  // TODO: HCL2 parser doesn't like the following line
//  multiline = (local.local_true) ?
//    "correct" : "wrong"

  // TODO: See test_hcl2_load_assumptions.py -> test_weird_ternary_string_clipping
  //       Doesn't currently pull the ternary correctly since it's evaluated inside the string.
//  bool_string_true  = "true" ? "correct" : "wrong"
//  bool_string_false = "false" ? "wrong" : "correct"

  // TODO: Comparison cases...
//  compare_string_true  = "a" == "a" ? "correct" : "wrong"
//  compare_string_false = "a" != "a" ? "wrong" : "correct"
//
//  compare_num_true  = 1 == 1 ? "correct" : "wrong"
//  compare_num_false = 1 != 1 ? "correct" : "wrong"
//
//  # NOTE: I don't think evals in locals is valid in TF, but the parser will eval it
//  default_not_taken = local.a != "" ? local.a : "default value"
//  default_taken     = local.empty != "" ? local.a : "default value"

  type        = bool
  default     = true
}