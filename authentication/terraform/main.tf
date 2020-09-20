###################
# HTTP API Gateway
###################

module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "${var.prefix}-auth-api"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["content-type", "x-amz-date", "authorization", "cookie", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
    allow_methods = ["*"]
    allow_origins = ["*"]
  }

  domain_name                 = "${var.prefix}.${var.domain_name}"
  domain_name_certificate_arn = module.acm.this_acm_certificate_arn

  integrations = {
    "GET /start-auth" = {
      lambda_arn             = module.start_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "GET /complete-auth" = {
      lambda_arn             = module.complete_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "$default" = {
      lambda_arn             = module.start_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }
  }
}

######
# Route53
######

data "aws_route53_zone" "this" {
  name = var.domain_name
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.prefix
  type    = "A"

  alias {
    name                   = module.api_gateway.this_apigatewayv2_domain_name_configuration.0.target_domain_name
    zone_id                = module.api_gateway.this_apigatewayv2_domain_name_configuration.0.hosted_zone_id
    evaluate_target_health = false
  }
}

######
# ACM
######

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 2.0"

  domain_name               = var.domain_name
  zone_id                   = data.aws_route53_zone.this.id
  subject_alternative_names = ["${var.prefix}.${var.domain_name}"]
}

######
# Lambda
######

module "complete_auth_lambda" {
  source          = "./modules/lambda"
  prefix          = var.prefix
  name            = "complete-auth"
  api_gateway_arn = module.api_gateway.this_apigatewayv2_api_execution_arn

  environment_variables = {
    THALIA_SERVER_URL    = var.thalia_server_url
    THALIA_CLIENT_ID     = var.thalia_client_id
    THALIA_CLIENT_SECRET = var.thalia_client_secret
    OAUTH_REDIRECT_URI   = "https://${var.prefix}.${var.domain_name}/complete-auth"
    DISCORD_GUILD_ID     = var.discord_guild_id
    USERS_TABLE          = split("/", var.users_table_arn)[1]
  }

  attach_policy_statements = true
  policy_statements = {
    dynamodb = {
      effect    = "Allow",
      actions   = ["dynamodb:PutItem"],
      resources = ["${var.users_table_arn}"]
    }
  }
}

module "start_auth_lambda" {
  source          = "./modules/lambda"
  prefix          = var.prefix
  name            = "start-auth"
  api_gateway_arn = module.api_gateway.this_apigatewayv2_api_execution_arn

  environment_variables = {
    THALIA_SERVER_URL    = var.thalia_server_url
    THALIA_CLIENT_ID     = var.thalia_client_id
    THALIA_CLIENT_SECRET = var.thalia_client_secret
    OAUTH_REDIRECT_URI   = "https://${var.prefix}.${var.domain_name}/complete-auth"
  }
}