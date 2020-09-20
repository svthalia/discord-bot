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

variable "discord_client_id" {
  type = string
}

variable "discord_client_secret" {
  type = string
}

variable "discord_bot_token" {
  type = string
}

variable "discord_bot_permissions" {
  type = string
}

variable "thalia_server_url" {
  type = string
}

variable "thalia_auth_client_id" {
  type = string
}

variable "thalia_bot_client_id" {
  type = string
}

variable "thalia_bot_client_secret" {
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