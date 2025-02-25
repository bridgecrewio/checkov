resource "test" "pass8" {
  range = ["1-5","2000-3100"]
}

resource "test" "pass1" {
  range = "*"
}

resource "test" "pass2" {
  range = 3000
}

resource "test" "pass3" {
  range = "3000"
}

resource "test" "pass4" {
  range = "3000-4000"
}

resource "test" "pass5" {
  range = "2000-3000"
}

resource "test" "pass6" {
  range = "2000-4000"
}

resource "test" "pass7" {
  range = ["2100","2000-4000","3400"]
}

resource "test" "fail1" {
  range = 2000
}

resource "test" "fail2" {
  range = "2000"
}

resource "test" "fail3" {
  range = "1000-2000"
}

resource "test" "fail4" {
  range = "4000-5000"
}

resource "test" "fail5" {
  # no range
}

resource "test" "fail6" {
  range = "abc"
}

resource "test" "fail7" {
  range = "abc-123"
}

resource "test" "fail8" {
  range = "1000-5000-6000"
}

resource "test" "fail9" {
  range = ["1000","2000-2900"]
}