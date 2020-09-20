locals {
  root_directory = "${abspath(path.module)}/../../../../.."
}

module "lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.prefix}-${var.name}"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"

  publish = true

  source_path = [
    {
      path             = "${local.root_directory}/common",
      prefix_in_zip    = "common",
    },
    {
      path = "${local.root_directory}/authentication/${var.name}-lambda"
      commands = [
        ":zip",
        "poetry export --format requirements.txt --without-hashes > requirements.txt",
        "cd `mktemp -d`",
        "python3 -m pip install --target=. -r ${local.root_directory}/authentication/${var.name}-lambda/requirements.txt",
        "rm ${local.root_directory}/authentication/${var.name}-lambda/requirements.txt",
        ":zip .",
      ],
      patterns = [
        "!poetry.lock",
        "!pyproject.toml",
        ""
      ]
    }
  ]

  attach_cloudwatch_logs_policy = true
  attach_policy_statements      = var.attach_policy_statements

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service = "apigateway"
      arn     = var.api_gateway_arn
    }
  }

  policy_statements = var.policy_statements

  environment_variables = var.environment_variables
}