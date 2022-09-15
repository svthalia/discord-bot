terraform {
  required_version = ">=1.2.9"
  backend "s3" {
    bucket = "thalia-terraform-state"
    key    = "discord-bot/production.tfstate"
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
  source = "../../modules/bot"
  prefix = var.prefix
  stage  = var.stage
  tags   = var.aws_tags
}

module "discord_bot_authentication" {
  source      = "../../modules/authentication"
  prefix      = var.prefix
  stage       = var.stage
  domain_name = var.domain_name
  tags        = var.aws_tags

  thalia_server_url    = var.thalia_server_url
  thalia_client_id     = var.thalia_auth_client_id
  thalia_client_secret = var.thalia_auth_client_secret

  discord_guild_id       = var.discord_guild_id
  discord_bot_token      = var.discord_bot_token
  discord_excluded_roles = var.discord_excluded_roles

  users_table_arn = module.discord_bot_common.users_table_arn
}
