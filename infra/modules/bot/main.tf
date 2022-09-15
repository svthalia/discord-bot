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

  tags = var.tags
}

####################
# HTTP API Gateway #
####################

resource "aws_cloudwatch_log_group" "logs" {
  name = "${var.prefix}-api"

  tags = var.tags
}

module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "${var.prefix}-auth-api"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["*"]
    allow_methods = ["*"]
    allow_origins = ["*"]
  }

  domain_name                 = "${var.prefix}.${var.domain_name}"
  domain_name_certificate_arn = module.acm.acm_certificate_arn

  default_stage_access_log_destination_arn = aws_cloudwatch_log_group.logs.arn
  default_stage_access_log_format          = "$context.identity.sourceIp - $context.requestTime - $context.routeKey $context.protocol - $context.status $context.responseLength $context.requestId $context.integrationErrorMessage"

  integrations = {
    "GET /start-auth" = {
      lambda_arn             = module.start_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }

    "GET /complete-auth" = {
      lambda_arn             = module.complete_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 29000
    }

    "POST /event" = {
      lambda_arn             = module.event_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 29000
    }

    "$default" = {
      lambda_arn             = module.start_auth_lambda.function_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 12000
    }
  }

  tags = var.tags
}

###########
# Route53 #
###########

data "aws_route53_zone" "this" {
  name = var.domain_name
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.prefix
  type    = "A"

  alias {
    name                   = module.api_gateway.apigatewayv2_domain_name_configuration[0].target_domain_name
    zone_id                = module.api_gateway.apigatewayv2_domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

#######
# ACM #
#######

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  domain_name               = var.domain_name
  zone_id                   = data.aws_route53_zone.this.id
  subject_alternative_names = ["${var.prefix}.${var.domain_name}"]

  tags = var.tags
}
