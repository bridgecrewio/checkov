# Example of HCL1 syntax that won't parse in HCL2
# (from https://github.com/amplify-education/python-hcl2/issues/13)

output "ebs_sizes" {
  value = {
    "x" : 600,
    "y" : 350,
    "z" : 350,
    "xx" : 200
  }
}