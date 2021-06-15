resource "local_file" "npmrc" {
  content  = "no"
  filename = ".npmrc"
}