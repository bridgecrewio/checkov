# Case 1: Pass: Default value for 'classic_access' is false

resource "ibm_is_vpc" "pass_1" {
  name = "pud-vpc"
}

# Case 2: Pass: 'classic_access' = 'false'
resource "ibm_is_vpc" "pass_2" {
  name = "pud-vpc"
  classic_access = false
}

# Case 3: Fail: 'classic_access' = 'true'

resource "ibm_is_vpc" "fail" {
  name = "pud-vpc"
  classic_access = true
}

