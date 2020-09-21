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

module "discord_bot_common" {
  source = "../../modules/common"
  prefix = var.prefix
  stage  = var.stage
}

module "discord_bot_authentication" {
  source      = "../../modules/authentication"
  prefix      = var.prefix
  stage       = var.stage
  domain_name = var.domain_name

  thalia_server_url    = var.thalia_server_url
  thalia_client_id     = var.thalia_auth_client_id
  thalia_client_secret = var.thalia_auth_client_secret

  discord_guild_id  = var.discord_guild_id
  discord_bot_token = var.discord_bot_token

  users_table_arn = module.discord_bot_common.users_table_arn
}

module "discord_bot_server" {
  source = "../../modules/bot"
  prefix = var.prefix
  stage  = var.stage

  thalia_server_url    = var.thalia_server_url
  thalia_client_id     = var.thalia_bot_client_id
  thalia_client_secret = var.thalia_bot_client_secret

  discord_guild_id        = var.discord_guild_id
  discord_bot_token       = var.discord_bot_token

  domain_name     = module.discord_bot_authentication.domain_name
  users_table_arn = module.discord_bot_common.users_table_arn
}
