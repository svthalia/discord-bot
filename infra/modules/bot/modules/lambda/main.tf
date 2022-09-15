locals {
  root_directory = "${abspath(path.module)}/../../../../.."
}

module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 4.0"

  function_name = "${var.prefix}-${var.name}"
  handler       = "index.lambdaHandler"
  runtime       = "nodejs16.x"
  memory_size   = 256
  timeout       = 30

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

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${var.api_gateway_arn}/*/*/*"
    },
    AllowExecutionFromAPIGatewayRoot = {
      service    = "apigateway"
      source_arn = "${var.api_gateway_arn}/*/*"
    }
  }

  policy_statements = var.policy_statements

  environment_variables = var.environment_variables
  tags                  = var.tags
}
