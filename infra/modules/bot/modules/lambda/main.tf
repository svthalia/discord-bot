locals {
  root_directory = "${abspath(path.module)}/../../../../.."
}

module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 4.0"

  function_name = "${var.prefix}-${var.name}"
  handler       = "index.lambdaHandler"
  runtime       = "nodejs16.x"
  memory_size   = var.memory
  timeout       = var.timeout

  publish = true

  source_path = [
    {
      path             = "${local.root_directory}/dist/${var.path}"
      npm_requirements = false
      # npm_requirements = true  # Will run "npm install" with package.json
    },
    {
      path             = "${local.root_directory}/node_modules"
      npm_requirements = false
    },
    {
      path             = "${local.root_directory}/dist/common"
      npm_requirements = false
    }
  ]

  attach_cloudwatch_logs_policy = true
  attach_policy_statements      = var.attach_policy_statements

  allowed_triggers = merge(var.api_gateway_arn != null ? {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${var.api_gateway_arn}/*/*/*"
    },
    AllowExecutionFromAPIGatewayRoot = {
      service    = "apigateway"
      source_arn = "${var.api_gateway_arn}/*/*"
    }
    } : {}, var.schedule_expression != null ? {
    OneRule = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.rule.0.arn
    }
    } : {

  })

  policy_statements = var.policy_statements

  environment_variables = var.environment_variables
  tags                  = var.tags
}

resource "aws_cloudwatch_event_rule" "rule" {
  count               = var.schedule_expression != null ? 1 : 0
  name                = "${var.prefix}-${var.name}-rule"
  schedule_expression = var.schedule_expression
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "target" {
  count = var.schedule_expression != null ? 1 : 0
  rule  = aws_cloudwatch_event_rule.rule.0.name
  arn   = module.lambda.lambda_function_arn
}
