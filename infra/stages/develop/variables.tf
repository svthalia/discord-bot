variable "prefix" {
  description = "Name to be used on all the resources as identifier"
  type        = string
}

variable "stage" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "discord_guild_id" {
  type = string
}

variable "discord_bot_token" {
  type = string
}

variable "discord_app_id" {
  type = string
}

variable "discord_public_key" {
  type = string
}

variable "discord_excluded_roles" {
  type = string
}

variable "thalia_server_url" {
  type = string
}

variable "thalia_auth_client_id" {
  type = string
}

variable "thalia_auth_client_secret" {
  type = string
}

variable "thalia_backend_client_id" {
  type = string
}

variable "thalia_backend_client_secret" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "aws_profile" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "aws_tags" {
  type = map(string)
}
