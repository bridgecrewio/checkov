resource "x" "pass1" {
  arr = [
    "allowed1"
  ]
}

resource "x" "pass2" {
  arr = [
  ]
}

resource "x" "pass3" {
  arr = [
    "allowed3",
    "allowed1"
  ]
}

resource "x" "pass4" {
  arr = "allowed2"
}

resource "x" "fail1" {
  arr = [
    "xxx"
  ]
}

resource "x" "fail2" {
  arr = [
    "xxx",
    "yyy"
  ]
}

resource "x" "fail3" {
  arr = [
    "xxx",
    "allowed1"
  ]
}

resource "x" "fail4" {
  arr = "xxx"
}

