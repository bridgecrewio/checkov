resource "aws_xyz" "pass1" {
  arr = [
    "allowed1"
  ]
  a_string = "abc"
}

resource "aws_xyz" "pass2" {
  arr = [
    "allowed1",
    "allowed3"
  ]
}

resource "aws_xyz" "pass3" {
  arr = [
  ]
}

//resource "aws_xyz" "fail1" {
//  arr = [
//    "allowed1",
//    "notallowed"
//  ]
//}

resource "aws_xyz" "fail2" {
  arr = [
    "notallowed",
    "alsonotallowed"
  ]
}

resource "aws_xyz" "fail3" {
  arr = [
    "notallowed"
  ]
}

