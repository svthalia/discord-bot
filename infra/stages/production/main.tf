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

  domain_name = var.domain_name

  thalia_server_url            = var.thalia_server_url
  thalia_auth_client_id        = var.thalia_auth_client_id
  thalia_auth_client_secret    = var.thalia_auth_client_secret
  thalia_backend_client_id     = var.thalia_backend_client_id
  thalia_backend_client_secret = var.thalia_backend_client_secret

  discord_guild_id       = var.discord_guild_id
  discord_app_id         = var.discord_app_id
  discord_public_key     = var.discord_public_key
  discord_bot_token      = var.discord_bot_token
  discord_excluded_roles = var.discord_excluded_roles
}
