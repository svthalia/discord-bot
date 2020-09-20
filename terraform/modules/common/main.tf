module "users_table" {
  source = "terraform-aws-modules/dynamodb-table/aws"

  name     = "${var.prefix}-users"
  hash_key = "thalia_user_id"

  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5

  attributes = [
    {
      name = "thalia_user_id"
      type = "S"
    },
    {
      name = "discord_user_id"
      type = "S"
    }
  ]

  global_secondary_indexes = [
    {
      name            = "DiscordIndex"
      hash_key        = "discord_user_id"
      projection_type = "ALL"
      write_capacity  = 5
      read_capacity   = 5
    }
  ]
}