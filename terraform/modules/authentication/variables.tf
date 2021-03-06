variable "stage" {
  type = string
}

variable "tags" {
  type = map(string)
}

variable "prefix" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "discord_bot_token" {
  type = string
}

variable "discord_guild_id" {
  type = string
}

variable "discord_excluded_roles" {
  type = string
}

variable "thalia_server_url" {
  type = string
}

variable "thalia_client_id" {
  type = string
}

variable "thalia_client_secret" {
  type = string
}

variable "users_table_arn" {
  type = string
}