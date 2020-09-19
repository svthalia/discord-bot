module "lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${var.name}-save-data"
  handler       = "index.lambda_handler"
  runtime       = "python3.8"

  source_path = [
    {
      path = "${path.module}/../../../src/save-data-lambda"
      commands = [
        ":zip",
        "poetry export --format requirements.txt --without-hashes > requirements.txt",
        "cd `mktemp -d`",
        "python3 -m pip install --target=. -r ${abspath(path.module)}/../../../src/save-data-lambda/requirements.txt",
        "rm ${abspath(path.module)}/../../../src/save-data-lambda/requirements.txt",
        ":zip .",
      ],
      patterns = [
        "!poetry.lock",
        "!pyproject.toml",
        ""
      ]
    }
  ]

}