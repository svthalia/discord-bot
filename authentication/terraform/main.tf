module "save-data-lambda" {
  source = "./modules/save-data-lambda"
  name   = var.name
  stage  = var.stage
}