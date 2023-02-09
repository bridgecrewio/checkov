resource "x" "x1" {
  list = ["a", "list", "of values"]
  dict = {
    another = "another"
    a_key = "a value"
  }
  complex = [
    {
      key = "value"
      key2 = "value2"
      listkey = ["list1", "list2"]
    },
    {
      key = "value22"
      key2 = "value22"
      listkey = ["listx", "listy"]
    }
  ]
}

resource "x" "x2" {
  list = ["a", "list", "of values"]
  dict = {
    another = "another"
    a_key = "a value"
  }
  complex = [
    {
      key = "value"
      key2 = "value2"
      listkey = ["list1", "list2"]
    },
    {
      key = "value22"
      key2 = "value22"
    }
  ]
}