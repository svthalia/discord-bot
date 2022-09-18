module "complete_auth_lambda" {
  source          = "./modules/lambda"
  prefix          = var.prefix
  name            = "complete-auth"
  path            = "authentication/complete"
  api_gateway_arn = module.api_gateway.apigatewayv2_api_execution_arn
  timeout         = 30

  environment_variables = {
    THALIA_SERVER_URL      = var.thalia_server_url
    THALIA_CLIENT_ID       = var.thalia_auth_client_id
    THALIA_CLIENT_SECRET   = var.thalia_auth_client_secret
    OAUTH_REDIRECT_URI     = "https://${var.prefix}.${var.domain_name}/complete-auth"
    DISCORD_GUILD_ID       = var.discord_guild_id
    DISCORD_BOT_TOKEN      = var.discord_bot_token
    DISCORD_EXCLUDED_ROLES = var.discord_excluded_roles
    USERS_TABLE            = split("/", module.users_table.dynamodb_table_arn)[1]
  }

  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect = "Allow",
      actions = [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      resources = [module.users_table.dynamodb_table_arn]
    }
  }

  tags = var.tags
}

module "start_auth_lambda" {
  source          = "./modules/lambda"
  prefix          = var.prefix
  name            = "start-auth"
  path            = "authentication/start"
  api_gateway_arn = module.api_gateway.apigatewayv2_api_execution_arn
  timeout         = 30

  environment_variables = {
    THALIA_SERVER_URL    = var.thalia_server_url
    THALIA_CLIENT_ID     = var.thalia_auth_client_id
    THALIA_CLIENT_SECRET = var.thalia_auth_client_secret
    OAUTH_REDIRECT_URI   = "https://${var.prefix}.${var.domain_name}/complete-auth"
    DISCORD_GUILD_ID     = var.discord_guild_id
    DISCORD_BOT_TOKEN    = var.discord_bot_token # Can be removed
  }

  tags = var.tags
}

module "event_lambda" {
  source          = "./modules/lambda"
  prefix          = var.prefix
  name            = "interaction-event"
  path            = "bot"
  api_gateway_arn = module.api_gateway.apigatewayv2_api_execution_arn
  timeout         = 300
  memory          = 512

  environment_variables = {
    THALIA_SERVER_URL      = var.thalia_server_url
    THALIA_CLIENT_ID       = var.thalia_backend_client_id
    THALIA_CLIENT_SECRET   = var.thalia_backend_client_secret
    DISCORD_GUILD_ID       = var.discord_guild_id
    DISCORD_APP_ID         = var.discord_app_id
    DISCORD_PUBLIC_KEY     = var.discord_public_key
    DISCORD_BOT_TOKEN      = var.discord_bot_token
    DISCORD_EXCLUDED_ROLES = var.discord_excluded_roles
    DOMAIN_NAME            = "https://${var.prefix}.${var.domain_name}/"
    USERS_TABLE            = split("/", module.users_table.dynamodb_table_arn)[1]
  }

  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect = "Allow",
      actions = [
        "dynamodb:DescribeTable",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem"
      ],
      resources = [module.users_table.dynamodb_table_arn, "${module.users_table.dynamodb_table_arn}/*"]
    }
  }

  tags = var.tags
}

module "sync_lambda" {
  source              = "./modules/lambda"
  prefix              = var.prefix
  name                = "scheduled-sync"
  path                = "scheduled/sync"
  timeout             = 300
  memory              = 512
  schedule_expression = "rate(1 hour)"

  environment_variables = {
    THALIA_SERVER_URL      = var.thalia_server_url
    THALIA_CLIENT_ID       = var.thalia_backend_client_id
    THALIA_CLIENT_SECRET   = var.thalia_backend_client_secret
    DISCORD_GUILD_ID       = var.discord_guild_id
    DISCORD_PUBLIC_KEY     = var.discord_public_key
    DISCORD_BOT_TOKEN      = var.discord_bot_token
    DISCORD_EXCLUDED_ROLES = var.discord_excluded_roles
    DOMAIN_NAME            = "https://${var.prefix}.${var.domain_name}/"
    USERS_TABLE            = split("/", module.users_table.dynamodb_table_arn)[1]
  }

  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect = "Allow",
      actions = [
        "dynamodb:DescribeTable",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem"
      ],
      resources = [module.users_table.dynamodb_table_arn, "${module.users_table.dynamodb_table_arn}/*"]
    }
  }

  tags = var.tags
}
