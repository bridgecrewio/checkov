resource "local_file" "npmrc" {
  content  = "//registry.npmjs.org/:_authToken=64ccf66c-21c9-4faa-bddd-6e4ad2a5a127"
  filename = ".npmrc"
}