terraform {
  required_version = "0.13.2"
  backend "s3" {
    bucket = "discord-bot-terraform"
    key    = "develop.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  profile             = var.aws_profile
  region              = var.aws_region
  allowed_account_ids = [var.aws_account_id]

  # assume_role {
  #   role_arn = "arn:aws:iam::${var.account_id}:role/Discord-Bot-Deployment"
  # }
}

module "discord-bot-authentication" {
  source = "../../../authentication/terraform"
  name   = var.name
  stage  = var.stage
}

module "discord-bot-server" {
  source = "../../../bot/terraform"
  name   = var.name
  stage  = var.stage
}
