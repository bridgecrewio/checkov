resource "xyz" "pass" {
  arr {
    name = "a"
    value = "a"
  }
  arr {
    name = "b"
    value = "x"
  }
}

resource "xyz" "fail" {
  arr {
    name = "b"
    value = "x"
  }
}