locals {
  root_directory = "${abspath(path.module)}/../../../../.."
}

module "lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.prefix}-${var.name}"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"
  memory_size   = 256
  timeout       = 30

  publish = true

  source_path = [
    {
      path          = "${local.root_directory}/common",
      prefix_in_zip = "common",
    },
    {
      path = "${local.root_directory}/authentication/${var.name}-lambda"
      commands = [
        ":zip",
        "cd ${local.root_directory}",
        "mkdir ${local.root_directory}/python",
        "poetry export --format requirements.txt --without-hashes > ${local.root_directory}/python/requirements.txt",
        "cd ${local.root_directory}/python",
        "docker run --rm -v $(pwd):/build -w /build lambci/lambda:build-python3.8 pip install -r requirements.txt -t .",
        "rm requirements.txt",
        ":zip .",
        "rm -rf ${local.root_directory}/python",
      ],
      patterns = [
        "!poetry.lock",
        "!pyproject.toml",
        "!.venv/.*"
      ]
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