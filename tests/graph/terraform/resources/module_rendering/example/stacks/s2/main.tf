module "mock" {
  source = "../../modules/mock"
}

module "second-mock" {
  source = "../../modules/second-mock"
  input = module.mock.o1
}